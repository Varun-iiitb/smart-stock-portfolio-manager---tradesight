module com.example.tradesight {
    requires javafx.controls;
    requires javafx.fxml;
    requires javafx.web;
    requires com.google.gson;
    requires java.net.http;
    requires java.desktop;
    requires java.sql;

    opens com.example.tradesight to javafx.fxml;
    exports com.example.tradesight;
}
