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

 Image {
	 id: image
	 x: 141
	 y: 64
	 width: 318
	 height: 272
	 fillMode: Image.PreserveAspectFit
	 source: "../output/inner.png"
 }
}
