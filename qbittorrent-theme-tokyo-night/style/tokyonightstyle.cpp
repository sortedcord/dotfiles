#include <QColor>
#include <QEvent>
#include <QPaintEvent>
#include <QPainter>
#include <QProxyStyle>
#include <QStyleFactory>
#include <QStylePlugin>
#include <QWidget>

namespace {

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

class TokyoNightStyle final : public QProxyStyle {
    TranslucentBgFilter *m_filter;

public:
    TokyoNightStyle()
        : QProxyStyle(QStyleFactory::create(QStringLiteral("Fusion")))
        , m_filter(new TranslucentBgFilter(this)) {}

    void polish(QWidget *w) override {
        if (w && w->isWindow()) {
            w->setAttribute(Qt::WA_TranslucentBackground, true);
            w->removeEventFilter(m_filter);
            w->installEventFilter(m_filter);
        }
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
