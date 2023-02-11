from gui import MainWindow, QApplication, sys
# con = QSqlDatabase.addDatabase("QSQLITE")
# con.setDatabaseName("tasks.sqlite")

# if not con.open():
#     print("Database Error: %s" % con.lastError().databaseText())
#     sys.exit(1)
app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec()