import QtQuick 2.14
import QtQuick.Controls 2.14

Page {
	width: 600
	height: 400

	title: qsTr("Page 1")

	Label {
		text: qsTr("You are on Page 1.")
		anchors.centerIn: parent
	}
}
