package com.example.tradesight;

import javafx.beans.value.ChangeListener;
import javafx.geometry.Insets;
import javafx.geometry.Pos;
import javafx.scene.Parent;
import javafx.scene.Scene;
import javafx.scene.control.Button;
import javafx.scene.control.ComboBox;
import javafx.scene.control.Label;
import javafx.scene.control.TextField;
import javafx.scene.layout.BorderPane;
import javafx.scene.layout.HBox;
import javafx.scene.layout.VBox;
import javafx.stage.Stage;

import java.io.IOException;
import java.util.Map;

public class dashboard {

    public Parent getlayout(String username, Stage window) {
        BorderPane root = new BorderPane();

        VBox sidepane = new VBox(10);
        sidepane.setPadding(new Insets(40, 20, 40, 20));
        sidepane.setPrefWidth(300);
        sidepane.setSpacing(40);
        sidepane.setStyle("-fx-background-color: #2c3e50;");

        Label title = new Label("Portfolio Manager");
        title.setId("sidebar-title");
        title.setAlignment(Pos.TOP_CENTER);

        Button dashboard = new Button("📊 Dashboard");
        Button Portfolio = new Button("💼 Portfolio");
        Button analysis = new Button("📈 Analysis");
        Button research = new Button("🔍 Research");

        dashboard.setPrefWidth(180);
        Portfolio.setPrefWidth(180);
        analysis.setPrefWidth(180);
        research.setPrefWidth(180);

        dashboard.getStyleClass().add("sidebar-buttons");
        Portfolio.getStyleClass().add("sidebar-buttons");
        analysis.getStyleClass().add("sidebar-buttons");
        research.getStyleClass().add("sidebar-buttons");

        dashboard.getStyleClass().add("nav-button-active");
        Portfolio.getStyleClass().add("sidebar-item");
        analysis.getStyleClass().add("sidebar-item");
        research.getStyleClass().add("sidebar-item");

        sidepane.getChildren().addAll(title, dashboard, Portfolio, analysis, research);
        sidepane.setAlignment(Pos.TOP_CENTER);
        root.setLeft(sidepane);

        VBox maincontent = new VBox(10);
        maincontent.setSpacing(30);

        Label heading = new Label("Portfolio Dashboard");
        heading.getStyleClass().add("main-content-heading");

        HBox buttons = new HBox(20);
        Button refresh_data = new Button("Refresh Data");
        refresh_data.getStyleClass().add("buttons");
        Button export = new Button("Export Data");
        export.getStyleClass().add("buttons");
        buttons.getChildren().addAll(refresh_data, export);

        export.setOnAction(event -> {
            dashboard_request.export_data(username);
        });

        VBox portfoliovalue = new VBox(10);
        portfoliovalue.setPadding(new Insets(20));
        portfoliovalue.setSpacing(10);
        portfoliovalue.setAlignment(Pos.CENTER_LEFT);
        portfoliovalue.getStyleClass().add("maincontent-vbox");
        portfoliovalue.prefWidth(100);
        Label label1 = new Label("Total Portfolio value");
        label1.getStyleClass().add("vbox-text");
        Label portfolio_balance_label = new Label();
        portfolio_balance_label.getStyleClass().add("vbox-text");
        portfoliovalue.getChildren().addAll(label1, portfolio_balance_label);

        VBox profitloss = new VBox(10);
        profitloss.setPadding(new Insets(20));
        profitloss.setSpacing(10);
        profitloss.getStyleClass().add("maincontent-vbox");
        Label profitloss_Label = new Label("Today's P&L");
        profitloss_Label.getStyleClass().add("vbox-text");
        Label profit_loss_label = new Label();
        profit_loss_label.getStyleClass().add("vbox-text");
        profitloss.getChildren().addAll(profitloss_Label, profit_loss_label);

        VBox Investment = new VBox(10);
        Investment.setPadding(new Insets(20));
        Investment.setSpacing(10);
        Investment.getStyleClass().add("maincontent-vbox");
        Label investment = new Label("Total Investment");
        investment.getStyleClass().add("vbox-text");
        Label investment_value_label = new Label();
        investment_value_label.getStyleClass().add("vbox-text");
        Investment.getChildren().addAll(investment, investment_value_label);

        refresh_data.setOnAction(event -> {
            String temp = String.valueOf(dashboard_request.portfolio_value(username));
            portfolio_balance_label.setText("₹" + temp);
            if (Double.parseDouble(temp) >= 0) {
                portfolio_balance_label.setStyle("-fx-text-fill: green");
            } else {
                portfolio_balance_label.setStyle("-fx-text-fill: red");
            }

            double temp1 = dashboard_request.profit_loss(username);
            if (temp1 >= 0) {
                profit_loss_label.setText("₹" + temp1);
                profit_loss_label.setStyle("-fx-text-fill: green");
            } else {
                profit_loss_label.setText("₹" + temp1);
                profit_loss_label.setStyle("-fx-text-fill: red");
            }

            double temp3 = dashboard_request.total_investment(username);
            investment_value_label.setText("₹" + temp3);
            investment_value_label.setStyle("-fx-text-fill: green");
        });

        // Load once initially
        refresh_data.fire();

        VBox ExchangeRates = new VBox(10);
        ExchangeRates.setSpacing(10);
        ExchangeRates.setPadding(new Insets(20));
        Label exchange = new Label("Exchange");
        exchange.getStyleClass().add("vbox-text");

        HBox exchange_entry = new HBox(10);
        TextField value = new TextField("1");
        value.getStyleClass().add("exchange-input");
        ComboBox<String> combobox = new ComboBox<>();
        combobox.getStyleClass().add("exchange");
        combobox.setPromptText("INR");
        Map<String, String> currencies = dashboard_request.currency_list();
        combobox.getItems().addAll(currencies.keySet());
        exchange_entry.getChildren().addAll(value, combobox);

        HBox exchanged = new HBox(10);
        double standard_rate = dashboard_request.exchanged_value("INR", "USD");
        TextField value2 = new TextField(Double.toString(standard_rate));
        value2.getStyleClass().add("exchange-input");
        value2.setEditable(false);
        ComboBox<String> combobox2 = new ComboBox<>();
        combobox2.getStyleClass().add("exchange");
        combobox2.setPromptText("USD");
        Map<String, String> currencies2 = dashboard_request.currency_list();
        combobox2.getItems().addAll(currencies2.keySet());
        exchanged.getChildren().addAll(value2, combobox2);

        ChangeListener<Object> liveConverter = (obs, oldVal, newVal) -> {
            try {
                String baseName = combobox.getValue();
                String targetName = combobox2.getValue();
                String input = value.getText();
                if (baseName != null && targetName != null && !input.isEmpty()) {
                    String baseCode = currencies.get(baseName);
                    String targetCode = currencies2.get(targetName);
                    double amount = Double.parseDouble(input);
                    double rate = dashboard_request.exchanged_value(baseCode, targetCode);
                    value2.setText(String.format("%.2f", amount * rate));
                } else {
                    value2.setText("");
                }
            } catch (Exception ex) {
                value2.setText("");
            }
        };

        value.textProperty().addListener(liveConverter);
        combobox.valueProperty().addListener(liveConverter);
        combobox2.valueProperty().addListener(liveConverter);

        ExchangeRates.getChildren().addAll(exchange, exchange_entry, exchanged);
        ExchangeRates.getStyleClass().add("maincontent-vbox");

        maincontent.getChildren().addAll(heading, buttons, portfoliovalue, profitloss, Investment, ExchangeRates);
        maincontent.setPadding(new Insets(30, 30, 30, 40));
        maincontent.setStyle("-fx-background-color: #FFFFF0");
        root.setCenter(maincontent);

        Portfolio.setOnAction(event -> {
            portfolio port = new portfolio();
            Scene portscene = new Scene(port.getlayout(username, window));
            portscene.getStylesheets().add(getClass().getResource("/portfolio.css").toExternalForm());
            window.setScene(portscene);
            window.setFullScreen(true);
            window.setFullScreenExitHint("");
        });

        research.setOnAction(event -> {
            research res = new research();
            Scene resscene = new Scene(res.getlayout(username, window));
            resscene.getStylesheets().add(getClass().getResource("/research.css").toExternalForm());
            window.setScene(resscene);
            window.setFullScreen(true);
            window.setFullScreenExitHint("");
        });

        analysis.setOnAction(event -> {
            analytics_graph analytics = new analytics_graph();
            Scene analysisscene = null;
            analysisscene = new Scene(analytics.getlayout(username, window));
            analysisscene.getStylesheets().add(getClass().getResource("/analysiss.css").toExternalForm());
            window.setScene(analysisscene);
            window.setFullScreen(true);
            window.setFullScreenExitHint("");
        });

        return root;
    }
}
