import QtQuick 2.14
import QtQuick.Controls 2.14

ApplicationWindow
{
	id: window
	visible: true
	width: 640; height: 480
	title: qsTr("Kuxaku")

	header: ToolBar
	{
		contentHeight: toolButton.implicitHeight

		ToolButton
		{
			id: toolButton
			text: stackView.depth > 1 ? "\u25C0" : "\u2630"
			font.pixelSize: Qt.application.font.pixelSize * 1.6
			onClicked:
			{
				if (stackView.depth > 1)
					stackView.pop()
				else
					drawer.open()
			}
		}

		Label
		{
			text: stackView.currentItem.title
			anchors.centerIn: parent
		}
	}

	Drawer
	{
		id: drawer
		width: window.width * 0.66
		height: window.height

		Column
		{
			anchors.fill: parent

			ItemDelegate
			{
				text: qsTr("Inner Planets")
				width: parent.width
				onClicked:
				{
					stackView.push("Page1Form.ui.qml")
					drawer.close()
				}
			}
			ItemDelegate
			{
				text: qsTr("Outer Planets")
				width: parent.width
				onClicked:
				{
					stackView.push("Page2Form.ui.qml")
					drawer.close()
				}
			}
			ItemDelegate
			{
				text: qsTr("Communication Delay")
				width: parent.width
				onClicked:
				{
					stackView.push("Page3Form.ui.qml")
					drawer.close()
				}
			}
			ItemDelegate
			{
				text: qsTr("Travel Times")
				width: parent.width
				onClicked:
				{
					stackView.push("Page4Form.ui.qml")
					drawer.close()
				}
			}
		}
	}

	StackView
	{
		id: stackView
		initialItem: "HomeForm.ui.qml"
		anchors.fill: parent
	}
}
