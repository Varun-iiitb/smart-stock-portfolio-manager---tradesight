package com.example.tradesight;

import javafx.collections.FXCollections;
import javafx.collections.ObservableList;
import javafx.geometry.Insets;
import javafx.geometry.Pos;
import javafx.scene.Parent;
import javafx.scene.Scene;
import javafx.scene.control.*;
import javafx.scene.control.cell.PropertyValueFactory;
import javafx.scene.layout.BorderPane;
import javafx.scene.layout.HBox;
import javafx.scene.layout.VBox;
import javafx.stage.Stage;

import java.io.IOException;
import java.sql.Date;
import java.time.LocalDate;
import java.util.List;

public class portfolio {
    public Parent getlayout(String username, Stage window) {

        BorderPane root1 = new BorderPane();

        // LEFT BAR
        VBox sidepane = new VBox(10);
        sidepane.setPadding(new Insets(40,20,40,20));
        sidepane.setPrefWidth(300);
        sidepane.setSpacing(40);
        sidepane.setStyle("-fx-background-color: #2c3e50;");

        Label title1 = new Label("Portfolio Manager");
        title1.setId("sidebar-title");
        title1.setAlignment(Pos.TOP_CENTER);

        Button dashboard = new Button("📊 Dashboard");
        Button Portfolio = new Button("💼 Portfolio");
        Button analysis  = new Button("📈 Analysis");
        Button research  = new Button("🔍 Research");

        dashboard.setPrefWidth(180);
        Portfolio.setPrefWidth(180);
        analysis.setPrefWidth(180);
        research.setPrefWidth(180);

        dashboard.getStyleClass().add("sidebar-buttons");
        Portfolio.getStyleClass().add("sidebar-buttons");
        analysis.getStyleClass().add("sidebar-buttons");
        research.getStyleClass().add("sidebar-buttons");

        dashboard.getStyleClass().add("sidebar-item");
        Portfolio.getStyleClass().add("nav-button-active");
        analysis.getStyleClass().add("sidebar-item");
        research.getStyleClass().add("sidebar-item");




    sidepane.getChildren().addAll(title1,dashboard,Portfolio,analysis,research);
        sidepane.setAlignment(Pos.TOP_CENTER);
        root1.setLeft(sidepane);



        VBox root = new VBox(10);
        root.setPadding(new Insets(20));
        VBox.setMargin(root, new  Insets(40,0,20,0));
        root.setSpacing(40);
        Label title = new Label("Current Holdings");
        title.setAlignment(Pos.CENTER);
        title.getStyleClass().add("current-holdings");

        // Table setup
        TableView<product> table = new TableView<>();
        table.setFixedCellSize(40);

        TableColumn<product, String> namecolumn = new TableColumn<>("Stock Name");
        namecolumn.setMinWidth(200);
        namecolumn.setCellValueFactory(new PropertyValueFactory<>("stockname"));

        TableColumn<product, Integer> quantitycolumn = new TableColumn<>("Qty");
        quantitycolumn.setMinWidth(200);
        quantitycolumn.setCellValueFactory(new PropertyValueFactory<>("quantity"));

        TableColumn<product, Double> pricecolumn = new TableColumn<>("Buying Price");
        pricecolumn.setMinWidth(200);
        pricecolumn.setCellValueFactory(new PropertyValueFactory<>("pricebuy"));

        TableColumn<product,Double> datecolumn = new TableColumn<>("Date of purchase");
        datecolumn.setMinWidth(200);
        datecolumn.setCellValueFactory(new PropertyValueFactory<>("date"));

        TableColumn<product, Double> currpricecolumn = new TableColumn<>("Current Price");
        currpricecolumn.setMinWidth(200);
        currpricecolumn.setCellValueFactory(new PropertyValueFactory<>("currprice"));

        TableColumn<product, Double> profitcolumn = new TableColumn<>("P&L");
        profitcolumn.setMinWidth(200);
        profitcolumn.setCellValueFactory(new PropertyValueFactory<>("profitloss"));

        TableColumn<product, String> changecolumn = new TableColumn<>("Change");
        changecolumn.setMinWidth(200);
        changecolumn.setCellValueFactory(new PropertyValueFactory<>("change"));

        table.getColumns().addAll(namecolumn, quantitycolumn, pricecolumn, datecolumn, currpricecolumn, profitcolumn, changecolumn);

        // Initial data load
        ObservableList<product> data = FXCollections.observableArrayList();
        List<List<Object>> portfolio_details = dashboard_request.get_stock(username);

        for (List<Object> row : portfolio_details) {
            String stockname = (String) row.get(0);
            int quantity = ((Double) row.get(1)).intValue();
            double pricebought = (double) row.get(2);
            Date date = Date.valueOf((String) row.get(3));
            double currentprice = (double) row.get(4);
            double profitloss = (double) row.get(5);
            String change = (String) row.get(6);

            data.add(new product(stockname, quantity, pricebought, date, currentprice, profitloss, change));
        }

        table.setItems(data);

        // Inputs
        TextField stockinput = new TextField();
        stockinput.setPromptText("Enter stock name");
        stockinput.setMinWidth(200);
        stockinput.getStyleClass().add("user-btn");

        TextField quantityinput = new TextField();
        quantityinput.setPromptText("Enter quantity");
        quantityinput.setMinWidth(200);
        quantityinput.getStyleClass().add("user-btn");

        TextField pricebuyinput = new TextField();
        pricebuyinput.setPromptText("Enter buying price");
        pricebuyinput.setMinWidth(200);
        pricebuyinput.getStyleClass().add("user-btn");

        TextField dateofpurchaseinput = new TextField();
        dateofpurchaseinput.setPromptText("Enter date (YYYY-MM-DD)");
        dateofpurchaseinput.setMinWidth(200);
        dateofpurchaseinput.getStyleClass().add("user-btn");

        // Add button
        Button add_stock = new Button("Add Stock");
        add_stock.getStyleClass().add("add-stock");
        add_stock.setOnAction(e -> {
            try {
                String stock = stockinput.getText();
                int quantity = Integer.parseInt(quantityinput.getText());
                double price = Double.parseDouble(pricebuyinput.getText());
                LocalDate localDate = LocalDate.parse(dateofpurchaseinput.getText());

                List<Object> addstockdata = dashboard_request.add_Stock(
                        username, stock, quantity, price, localDate
                );

                product newProduct = new product(
                        (String) addstockdata.get(0),
                        ((Double) addstockdata.get(1)).intValue(),
                        (double) addstockdata.get(2),
                        Date.valueOf((String) addstockdata.get(3)),
                        (double) addstockdata.get(4),
                        (double) addstockdata.get(5),
                        (String) addstockdata.get(6)
                );

                data.add(newProduct); // updates table automatically

                // Clear inputs
                stockinput.clear();
                quantityinput.clear();
                pricebuyinput.clear();
                dateofpurchaseinput.clear();

            } catch (Exception ex) {
            }
        });


        HBox hbox = new HBox(10, stockinput, quantityinput, pricebuyinput, dateofpurchaseinput, add_stock);
        hbox.setPadding(new Insets(20));

        root.getChildren().addAll(title, table, hbox);
        root1.setCenter(root);

        research.setOnAction(event -> {
            research res = new research();
            Scene resscene = new Scene(res.getlayout(username,window));
            resscene.getStylesheets().add(getClass().getResource("/research.css").toExternalForm());
            window.setScene(resscene);
            window.setFullScreen(true);
            window.setFullScreenExitHint("");
        });

        analysis.setOnAction(event -> {
            analytics_graph analytics = new analytics_graph();
            Scene analysisscene = null;
            analysisscene = new Scene(analytics.getlayout(username,window));
            analysisscene.getStylesheets().add(getClass().getResource("/analysiss.css").toExternalForm());
            window.setScene(analysisscene);
            window.setFullScreen(true);
            window.setFullScreenExitHint("");
        });

        dashboard.setOnAction(event -> {
            com.example.tradesight.dashboard dash = new  com.example.tradesight.dashboard();
            Scene dashcene = new Scene(dash.getlayout(username,window));
            dashcene.getStylesheets().add(getClass().getResource("/styles.css").toExternalForm());
            window.setScene(dashcene);
            window.setFullScreen(true);
            window.setFullScreenExitHint("");
        });

        return root1;
    }
}
