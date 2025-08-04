package com.example.tradesight;

import com.google.gson.JsonObject;
import javafx.application.Platform;
import javafx.geometry.Insets;
import javafx.geometry.Pos;
import javafx.scene.Parent;
import javafx.scene.Scene;
import javafx.scene.control.*;
import javafx.scene.image.Image;      // <-- ADDED
import javafx.scene.image.ImageView;   // <-- ADDED
import javafx.scene.layout.*;
// REMOVED: import javafx.scene.web.WebEngine;
// REMOVED: import javafx.scene.web.WebView;
import javafx.scene.web.WebEngine;
import javafx.scene.web.WebView;
import javafx.stage.Stage;

import java.io.File;
import java.io.IOException;
import java.time.LocalDate;
// REMOVED: import java.util.Timer;
// REMOVED: import java.util.TimerTask;

public class research {

    public Parent getlayout(String username, Stage window) {

        BorderPane root = new BorderPane();

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
        Portfolio.getStyleClass().add("sidebar-item");
        analysis.getStyleClass().add("sidebar-item");
        research.getStyleClass().add("nav-button-active");

        sidepane.getChildren().addAll(title1,dashboard,Portfolio,analysis,research);
        sidepane.setAlignment(Pos.TOP_CENTER);
        root.setLeft(sidepane);

        VBox contentArea = new VBox(15); // Changed from 'container' to 'contentArea' for clarity within this scope
        contentArea.setAlignment(Pos.CENTER);
        contentArea.setPadding(new Insets(40));
//        contentArea.getStyleClass().add("root"); // Apply 'root' style to this content area

        // Initial content (Search bar section)
        Label icon = new Label("📈");
        icon.getStyleClass().add("icon-label");

        Label title = new Label("Start your research");
        title.getStyleClass().add("main-label");

        HBox searchSection = new HBox(10);
        searchSection.setAlignment(Pos.CENTER);

        TextField searchBar = new TextField();
        searchBar.setPromptText("Search stock name or code");
        searchBar.getStyleClass().add("search-bar");

        Button submitButton = new Button("Submit");
        submitButton.getStyleClass().add("submit-button");

        searchSection.getChildren().addAll(searchBar, submitButton);

        Label subtitle = new Label("Enter a stock name or code above to get insights");
        subtitle.getStyleClass().add("subtext-label");

        contentArea.getChildren().addAll(icon, title, searchSection, subtitle);


        submitButton.setOnAction(event -> {

            contentArea.getChildren().clear(); // Clear initial content
            contentArea.getChildren().add(searchSection); // Add search bar back

            String stockname = searchBar.getText();
            JsonObject stock = dashboard_request.detailed_stock(stockname);
            String symbol = stock.has("symbol") && !stock.get("symbol").isJsonNull() ? stock.get("symbol").getAsString() : "N/A";
            String exchange = stock.has("exchange") && !stock.get("exchange").isJsonNull() ? stock.get("exchange").getAsString() : "N/A";
            String name = stock.has("name") && !stock.get("name").isJsonNull() ? stock.get("name").getAsString() : "N/A";
            String industry = stock.has("industry") && !stock.get("industry").isJsonNull() ? stock.get("industry").getAsString() : "N/A";
            Double currprice = stock.has("currentPrice") && !stock.get("currentPrice").isJsonNull() ? stock.get("currentPrice").getAsDouble() : 0.0;
            Double previousClose = stock.has("previousClose") && !stock.get("previousClose").isJsonNull() ? stock.get("previousClose").getAsDouble() : 0.0;
            Double open = stock.has("open") && !stock.get("open").isJsonNull() ? stock.get("open").getAsDouble() : 0.0;
            Double high = stock.has("high") && !stock.get("high").isJsonNull() ? stock.get("high").getAsDouble() : 0.0;
            Double low = stock.has("low") && !stock.get("low").isJsonNull() ? stock.get("low").getAsDouble() : 0.0;
            Double peratio = stock.has("Pe_ratio") && !stock.get("Pe_ratio").isJsonNull() ? stock.get("Pe_ratio").getAsDouble() : 0.0;
            Double EPS = stock.has("EPS") && !stock.get("EPS").isJsonNull() ? stock.get("EPS").getAsDouble() : 0.0;
            Double weekhigh = stock.has("52_week_high") && !stock.get("52_week_high").isJsonNull() ? stock.get("52_week_high").getAsDouble() : 0.0;
            Double weeklow = stock.has("52_week_low") && !stock.get("52_week_low").isJsonNull() ? stock.get("52_week_low").getAsDouble() : 0.0;
            Double bookvalue = stock.has("bookValue") && !stock.get("bookValue").isJsonNull() ? stock.get("bookValue").getAsDouble() : 0.0;
            Double twohundredavg = stock.has("200avg") && !stock.get("200avg").isJsonNull() ? stock.get("200avg").getAsDouble() : 0.0;

            // group 1
            //-------------------------------------------------------------------------------------
            Label company = new Label(name + "(" + symbol + ")");
            company.getStyleClass().add("stock-heading");

            HBox hbox = new HBox();
            Label currentprice = new Label(currprice.toString());
            currentprice.getStyleClass().add("stock-heading");

            Double temp = currprice - previousClose;
            Double percenttemp = temp/previousClose*100;

            temp = Math.round(temp * 100.0) / 100.0;
            percenttemp = Math.round(percenttemp * 100.0) / 100.0;

            Label change;
            if (temp>0){
                change = new Label("+" + temp + " " + "(" + percenttemp +"%)");
                change.getStyleClass().add("change");
                change.setStyle("-fx-text-fill: green;");
            }
            else{
                change = new Label( temp + " " + "(" + percenttemp +"%)");
                change.getStyleClass().add("change");
                change.setStyle("-fx-text-fill: red;");
            }
            change.getStyleClass().add("stock-heading");

            hbox.getChildren().addAll(currentprice,change);
            hbox.setSpacing(10);
            hbox.setPadding(new Insets(10));
            // -------------------------------------------------------------------------------------------------------------

            // box2
            VBox box2 = new VBox();
            Label Prevclose = new Label("Previous close");
            Prevclose.getStyleClass().add("label-boxes");
            Label prevclose_value = new Label(previousClose.toString());
            HBox.setHgrow(prevclose_value, Priority.ALWAYS);
            prevclose_value.setMaxWidth(Double.MAX_VALUE);
            prevclose_value.setAlignment(Pos.CENTER_RIGHT);
            prevclose_value.getStyleClass().add("label-boxes-value");
            HBox row3 = new HBox(40);
            row3.getChildren().addAll(Prevclose,prevclose_value);

            Label Open = new Label("Open");
            Open.getStyleClass().add("label-boxes");
            Label open_value = new Label(open.toString());
            HBox.setHgrow(open_value, Priority.ALWAYS);
            open_value.setMaxWidth(Double.MAX_VALUE);
            open_value.setAlignment(Pos.CENTER_RIGHT);
            open_value.getStyleClass().add("label-boxes-value");
            HBox row4 = new HBox(40);
            row4.getChildren().addAll(Open,open_value);

            Label High = new Label("High");
            High.getStyleClass().add("label-boxes");
            Label high_value = new Label(high.toString());
            HBox.setHgrow(high_value, Priority.ALWAYS);
            high_value.setMaxWidth(Double.MAX_VALUE);
            high_value.setAlignment(Pos.CENTER_RIGHT);
            high_value.getStyleClass().add("label-boxes-value");
            HBox row5 = new HBox(40);
            row5.getChildren().addAll(High,high_value);

            Label Low = new Label("Low");
            Low.getStyleClass().add("label-boxes");
            Label low_value = new Label(low.toString());
            HBox.setHgrow(low_value, Priority.ALWAYS);
            low_value.setMaxWidth(Double.MAX_VALUE);
            low_value.setAlignment(Pos.CENTER_RIGHT);
            low_value.getStyleClass().add("label-boxes-value");
            HBox row6 = new HBox(40);
            row6.getChildren().addAll(Low,low_value);

            box2.getChildren().addAll(row3, new Separator(),row4, new Separator(),row5, new Separator(),row6);
            box2.getStyleClass().add("boxes");
            box2.setPrefWidth(500);
            box2.setSpacing(10);
            box2.setPadding(new Insets(20));
            //--------------------------------------------------------------------------------------------------------------

            // box3
            VBox box3 = new VBox();
            Label WeekHigh = new Label("52 Wk High");
            WeekHigh.getStyleClass().add("label-boxes");
            Label WeekHigh_value = new Label(weekhigh.toString());
            HBox.setHgrow(WeekHigh_value, Priority.ALWAYS);
            WeekHigh_value.setMaxWidth(Double.MAX_VALUE);
            WeekHigh_value.setAlignment(Pos.CENTER_RIGHT);
            WeekHigh_value.getStyleClass().add("label-boxes-value");
            HBox row7 = new HBox(20);
            row7.getChildren().addAll(WeekHigh,WeekHigh_value);

            Label WeekLow = new Label("52 Wk Low");
            WeekLow.getStyleClass().add("label-boxes");
            Label WeekLow_value = new Label(weeklow.toString());
            HBox.setHgrow(WeekLow_value, Priority.ALWAYS);
            WeekLow_value.setMaxWidth(Double.MAX_VALUE);
            WeekLow_value.setAlignment(Pos.CENTER_RIGHT);
            WeekLow_value.getStyleClass().add("label-boxes-value");
            HBox row8 = new HBox(20);
            row8.getChildren().addAll(WeekLow,WeekLow_value);

            Label PE = new  Label("PE ratio");
            PE.getStyleClass().add("label-boxes");
            Label PE_VALUE = new Label(peratio.toString());
            HBox.setHgrow(PE_VALUE, Priority.ALWAYS);
            PE_VALUE.setMaxWidth(Double.MAX_VALUE);
            PE_VALUE.setAlignment(Pos.CENTER_RIGHT);
            PE_VALUE.getStyleClass().add("label-boxes-value");
            HBox row9 = new HBox(20);
            row9.getChildren().addAll(PE,PE_VALUE);

            Label eps = new Label("EPS");
            eps.getStyleClass().add("label-boxes");
            Label eps_value = new Label(EPS.toString());
            HBox.setHgrow(eps_value, Priority.ALWAYS);
            eps_value.setMaxWidth(Double.MAX_VALUE);
            eps_value.setAlignment(Pos.CENTER_RIGHT);
            eps_value.getStyleClass().add("label-boxes-value");
            HBox row10 = new HBox(20);
            row10.getChildren().addAll(eps,eps_value);

            box3.getChildren().addAll(row7, new Separator(),row8, new Separator(),row9, new Separator(),row10);
            box3.getStyleClass().add("boxes");
            box3.setPrefWidth(500);
            box3.setSpacing(10);
            box3.setPadding(new Insets(20));
            //--------------------------------------------------------------------------------------------------------------

            // box 4
            VBox box4 = new VBox();
            Label Exchange = new  Label("Exchange");
            Exchange.getStyleClass().add("label-boxes");
            Label exchange_value = new Label(exchange);
            HBox.setHgrow(exchange_value, Priority.ALWAYS);
            exchange_value.setMaxWidth(Double.MAX_VALUE);
            exchange_value.setAlignment(Pos.CENTER_RIGHT);
            exchange_value.getStyleClass().add("label-boxes-value");
            HBox row11 = new HBox(20);
            row11.getChildren().addAll(Exchange,exchange_value);

            Label Industry =  new Label("Industry");
            Industry.getStyleClass().add("label-boxes");
            Label Industry_value = new Label(industry);
            HBox.setHgrow(Industry_value, Priority.ALWAYS);
            Industry_value.setMaxWidth(Double.MAX_VALUE);
            Industry_value.setAlignment(Pos.CENTER_RIGHT);
            Industry_value.getStyleClass().add("label-boxes-value");
            HBox row12 = new HBox(20);
            row12.getChildren().addAll(Industry,Industry_value);

            Label BookValue = new Label("Book Value");
            BookValue.getStyleClass().add("label-boxes");
            Label BookValue_value = new Label(bookvalue.toString());
            HBox.setHgrow(BookValue_value, Priority.ALWAYS);
            BookValue_value.setMaxWidth(Double.MAX_VALUE);
            BookValue_value.setAlignment(Pos.CENTER_RIGHT);
            BookValue_value.getStyleClass().add("label-boxes-value");
            HBox row13 = new HBox(20);
            row13.getChildren().addAll(BookValue,BookValue_value);

            Label two_hundred_avg = new Label("200avg");
            two_hundred_avg.getStyleClass().add("label-boxes");
            Label TWO_hundred_avg = new Label(twohundredavg.toString());
            HBox.setHgrow(TWO_hundred_avg, Priority.ALWAYS);
            TWO_hundred_avg.setMaxWidth(Double.MAX_VALUE);
            TWO_hundred_avg.setAlignment(Pos.CENTER_RIGHT);
            TWO_hundred_avg.getStyleClass().add("label-boxes-value");
            HBox row14 = new HBox(20);
            row14.getChildren().addAll(two_hundred_avg,TWO_hundred_avg);

            box4.getChildren().addAll(row11, new Separator(),row12, new Separator(),row13, new Separator(),row14);
            box4.getStyleClass().add("boxes");
            box4.setPrefWidth(500);
            box4.setSpacing(10);
            box4.setPadding(new Insets(20));


            HBox bigbox = new HBox();
            bigbox.setSpacing(30);
            bigbox.getChildren().addAll(box2,box3,box4);

            VBox top_half =  new VBox();
            top_half.setSpacing(20);
            top_half.getChildren().addAll(company,hbox,bigbox);

            // Corrected Path Resolution for backend directory
            // This will resolve 'backend' relative to the application's current working directory (tradesight_app)
            String currentAppDir = null; // This gets C:\Users\varun\OneDrive\Desktop\tradesight_app\tradesight
            try {
                currentAppDir = new File(".").getCanonicalPath();
            } catch (IOException e) {
                // Handle the exception appropriately, e.g., log it or show an error to the user
                System.err.println("Error getting current directory: " + e.getMessage());
                throw new RuntimeException("Could not resolve current directory", e);
            }
            // Get the parent directory (C:\Users\varun\OneDrive\Desktop\tradesight_app)
            File parentDir = new File(currentAppDir).getParentFile();

            // Now construct the correct path to the backend folder from the parent
            File backendDir = new File(parentDir, "backend");

            // --- CHART DISPLAY: Replaced WebView with ImageView ---
            dashboard_request.graph(stockname,LocalDate.now().minusDays(30),LocalDate.now()); // This call should trigger backend to save PNG

            WebView webView = new WebView();
            webView.setMinSize(800, 600);
            webView.setPrefSize(800, 600);
            webView.setMaxSize(Double.MAX_VALUE, Double.MAX_VALUE);

            WebEngine webEngine = webView.getEngine();







            Label Price = new  Label("Closing Price");
            Price.getStyleClass().add("stock-heading");
            HBox day_range =  new HBox();
            day_range.setSpacing(20);
            Button day_1 = new Button("1D");
            Button day_5 = new Button("5D");
            Button month_1 = new Button("1M");
            Button month_6 = new Button("6M");
            Button year_1 = new Button("1Y");
            Button year_5 = new Button("5Y");

            day_range.getChildren().addAll(day_1,day_5,month_1,month_6,year_1,year_5);

            // Runnable to update ImageView on date range button clicks
            Runnable reloadWebView = () -> {
                new java.util.Timer().schedule(new java.util.TimerTask() {
                    @Override
                    public void run() {
                        javafx.application.Platform.runLater(webEngine::reload);
                    }
                }, 500); // half a second delay
            };


            day_1.setOnAction(e ->{
                System.out.println("triggered");
                dashboard_request.graph(stockname,LocalDate.now().minusDays(1),LocalDate.now());
                reloadWebView.run();
            });

            day_5.setOnAction(e ->{
                System.out.println("triggered");
                dashboard_request.graph(stockname,LocalDate.now().minusDays(5),LocalDate.now());
                reloadWebView.run();
            });

            month_1.setOnAction(e ->{
                System.out.println("triggered");
                dashboard_request.graph(stockname,LocalDate.now().minusMonths(1),LocalDate.now());
                reloadWebView.run();
            });

            month_6.setOnAction(e ->{
                System.out.println("triggered");
                dashboard_request.graph(stockname,LocalDate.now().minusMonths(6),LocalDate.now());
                reloadWebView.run();
            });

            year_1.setOnAction(e ->{
                System.out.println("triggered");
                dashboard_request.graph(stockname,LocalDate.now().minusYears(1),LocalDate.now());
                reloadWebView.run();
            });

            year_5.setOnAction(e ->{
                System.out.println("triggered");
                dashboard_request.graph(stockname,LocalDate.now().minusYears(5),LocalDate.now());
                reloadWebView.run();
            });
            VBox centerChartSection = new VBox();
            centerChartSection.setSpacing(20);
            centerChartSection.setPadding(new Insets(20));
            centerChartSection.getChildren().addAll(Price, day_range, webView);
            centerChartSection.setVgrow(webView, Priority.ALWAYS);

            // Replace with the correct path to your HTML file
            File liveStockFile = new File(backendDir, "live_stock_prices.html");
            webEngine.load(liveStockFile.toURI().toString());

            webEngine.documentProperty().addListener((obs, oldDoc, newDoc) -> {
                if (newDoc != null) {
                    webEngine.executeScript("""
                    const firstChild = document.body.children[0];
                    if (firstChild) {
                        firstChild.style.width = '100%';
                        firstChild.style.height = '100%';
                        firstChild.style.display = 'flex';
                        firstChild.style.justifyContent = 'center';
                        firstChild.style.alignItems = 'center';
                    }
                    document.body.style.margin = '0';
                    document.body.style.padding = '0';
                """);
                }
            });





            Label prediction = new Label("Prediction of coming month");
            prediction.getStyleClass().add("stock-heading");
            String ml_output = dashboard_request.ml_prediction(stockname);

            Label ml_label = new Label(ml_output);
            ml_label.getStyleClass().add("prediction-label");

            // --- PREDICTION DISPLAY: Using WebView instead of ImageView ---
            WebView predictionWebView = new WebView();
            WebEngine predictionEngine = predictionWebView.getEngine();

// Load the local prediction HTML file
            File predictionHtmlFile = new File(backendDir, "prediction.html");
            if (predictionHtmlFile.exists()) {
                String url = predictionHtmlFile.toURI().toString();
                predictionEngine.load(url);

                // Resize the chart after it loads
                predictionEngine.documentProperty().addListener((obs, oldDoc, newDoc) -> {
                    if (newDoc != null) {
                        predictionEngine.executeScript("""
                const chart = document.body.children[0];
                if (chart) {
                    chart.style.width = '100%';
                    chart.style.height = '100%';
                    chart.style.display = 'flex';
                    chart.style.justifyContent = 'center';
                    chart.style.alignItems = 'center';
                }
                document.body.style.margin = '0';
                document.body.style.padding = '0';
            """);
                    }
                });

            } else {
                System.err.println("Prediction HTML file not found: " + predictionHtmlFile.getAbsolutePath());
            }


            VBox vbox1 = new VBox();
            vbox1.setSpacing(20);
            vbox1.getChildren().addAll(prediction,ml_label,predictionWebView); // Added predictionImageView
            contentArea.getChildren().addAll(top_half,centerChartSection,vbox1); // Added centerChartSection and vbox1 to contentArea
            contentArea.getStyleClass().add("root");

        });
        ScrollPane scrollPane = new ScrollPane();
        scrollPane.setContent(contentArea); // Set contentArea as the scroll pane content
        scrollPane.setFitToWidth(true);
        scrollPane.setPannable(true);
        root.setCenter(scrollPane);


        analysis.setOnAction(event -> {
            analytics_graph analytics = new analytics_graph();
            Scene analysisscene = null;
            analysisscene = new Scene(analytics.getlayout(username,window));
            analysisscene.getStylesheets().add(getClass().getResource("/analysiss.css").toExternalForm());
            window.setScene(analysisscene);
            window.setFullScreen(true);
            window.setFullScreenExitHint("");
        });

        Portfolio.setOnAction(event -> {
            portfolio port = new portfolio();
            Scene portscene = new Scene(port.getlayout(username,window));
            portscene.getStylesheets().add(getClass().getResource("/portfolio.css").toExternalForm());
            window.setScene(portscene);
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

        return root;
    }
}