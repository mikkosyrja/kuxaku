#include <QGuiApplication>
#include <QQmlApplicationEngine>

int main(int argc, char *argv[])
{
	QCoreApplication::setAttribute(Qt::AA_EnableHighDpiScaling);

	QGuiApplication app(argc, argv);

	QQmlApplicationEngine engine;
	const QUrl url(QStringLiteral("qrc:/main.qml"));

	auto function = [url](QObject *obj, const QUrl &objUrl)
	{
		if ( !obj && url == objUrl )
			QCoreApplication::exit(-1);
	};

	QObject::connect(&engine, &QQmlApplicationEngine::objectCreated, &app,
		function, Qt::QueuedConnection);
	engine.load(url);

	return app.exec();
}
