#include <QApplication>
#include <QColor>
#include <QEvent>
#include <QPaintEvent>
#include <QPainter>
#include <QProxyStyle>
#include <QStyleFactory>
#include <QStylePlugin>
#include <QSurfaceFormat>
#include <QWidget>
#include <QWindow>

namespace {

void ensureTranslucentWindow(QWidget *w, QObject *paintFilter) {
    if (!w || !w->isWindow())
        return;

    if (!w->testAttribute(Qt::WA_TranslucentBackground))
        w->setAttribute(Qt::WA_TranslucentBackground, true);

    if (auto *wh = w->windowHandle(); wh && wh->format().alphaBufferSize() < 8) {
        auto fmt = wh->format();
        fmt.setAlphaBufferSize(8);
        wh->setFormat(fmt);
        if (wh->handle()) {
            wh->destroy();
            wh->create();
        }
    }

    w->removeEventFilter(paintFilter);
    w->installEventFilter(paintFilter);
}

class TranslucentBgFilter final : public QObject {
public:
    using QObject::QObject;

    bool eventFilter(QObject *obj, QEvent *ev) override {
        if (ev->type() == QEvent::Paint) {
            if (auto *w = qobject_cast<QWidget *>(obj); w && w->isWindow()) {
                const auto *pe = static_cast<QPaintEvent *>(ev);
                QPainter p(w);
                p.setCompositionMode(QPainter::CompositionMode_Source);
                const Qt::WindowType wt = w->windowType();
                const QColor bg = (wt == Qt::Popup || wt == Qt::ToolTip)
                    ? QColor(0, 0, 0, 0)
                    : QColor(14, 16, 23, 217);
                p.fillRect(pe->rect(), bg);
            }
        }
        return false;
    }
};

class WindowCreateFilter final : public QObject {
    TranslucentBgFilter *m_paintFilter;

public:
    WindowCreateFilter(TranslucentBgFilter *paintFilter, QObject *parent)
        : QObject(parent)
        , m_paintFilter(paintFilter) {}

    bool eventFilter(QObject *obj, QEvent *ev) override {
        if (ev->type() == QEvent::WinIdChange || ev->type() == QEvent::Show) {
            if (auto *w = qobject_cast<QWidget *>(obj); w && w->isWindow())
                ensureTranslucentWindow(w, m_paintFilter);
        }
        return false;
    }
};

class TokyoNightStyle final : public QProxyStyle {
    TranslucentBgFilter *m_paintFilter;
    WindowCreateFilter *m_createFilter;

public:
    TokyoNightStyle()
        : QProxyStyle(QStyleFactory::create(QStringLiteral("Fusion")))
        , m_paintFilter(new TranslucentBgFilter(this))
        , m_createFilter(new WindowCreateFilter(m_paintFilter, this)) {
        QSurfaceFormat fmt = QSurfaceFormat::defaultFormat();
        fmt.setAlphaBufferSize(8);
        QSurfaceFormat::setDefaultFormat(fmt);
        if (qApp)
            qApp->installEventFilter(m_createFilter);
    }

    void polish(QWidget *w) override {
        ensureTranslucentWindow(w, m_paintFilter);
        QProxyStyle::polish(w);
    }
};

} // namespace

class TokyoNightStylePlugin final : public QStylePlugin {
    Q_OBJECT
    Q_PLUGIN_METADATA(IID "org.qt-project.Qt.QStyleFactoryInterface" FILE "tokyonight.json")

public:
    QStyle *create(const QString &key) override {
        if (key.compare(QStringLiteral("tokyonight"), Qt::CaseInsensitive) == 0)
            return new TokyoNightStyle();
        return nullptr;
    }
};

#include "tokyonightstyle.moc"
