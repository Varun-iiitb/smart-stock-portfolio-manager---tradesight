package com.example.tradesight;

import com.google.gson.Gson;
import com.google.gson.JsonObject;
import com.google.gson.reflect.TypeToken;

import java.awt.*;
import java.lang.reflect.Type;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.time.LocalDate;
import java.util.*;
import java.util.List;


public class dashboard_request {

    public static void export_data(String username){
        try{
            String jsonbody = String.format("{\"username\":\"%s\"}", username);

            HttpRequest request = HttpRequest.newBuilder().uri(URI.create("http://localhost:5000/export")).header("Content-Type", "application/json").POST(HttpRequest.BodyPublishers.ofString(jsonbody)).build();
            HttpClient httpClient = HttpClient.newHttpClient();
            HttpResponse<byte []> response = httpClient.send(request, HttpResponse.BodyHandlers.ofByteArray());
            Path path = Paths.get(System.getProperty("user.home"), "Desktop", "report.xlsx");
            Files.write(path, response.body());

            // Open the file
            Desktop.getDesktop().open(path.toFile());
        } catch (Exception e) {
            throw new RuntimeException(e);
        }
    }

    public static List<Object> add_Stock(String username, String stock_name, int quantity, double price, LocalDate date) {
        try {
            String jsonbody = String.format("{\"username\":\"%s\",\"stock_name\":\"%s\",\"quantity\":\"%d\",\"price_per_share\":\"%f\",\"date\":\"%s\"}",username,stock_name, quantity, price,date);

            HttpRequest request = HttpRequest.newBuilder().uri(URI.create("http://localhost:5000/add_stock")).header("Content-Type", "application/json").POST(HttpRequest.BodyPublishers.ofString(jsonbody)).build();
            HttpClient httpClient = HttpClient.newHttpClient();
            HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());
            Gson gson = new Gson();
            List<Object> addstockdata = gson.fromJson(response.body(), new TypeToken<List<Object>>() {
            }.getType());
            return addstockdata;
        } catch (Exception e) {
            return new ArrayList<>();
        }
    }

    public static double portfolio_value(String username) {
        try {
            String jsonbody = String.format("{\"username\":\"%s\"}", username);

            HttpRequest request = HttpRequest.newBuilder().uri(URI.create("http://localhost:5000/portfolio_value_today")).header("Content-Type", "application/json").POST(HttpRequest.BodyPublishers.ofString(jsonbody)).build();
            HttpClient httpClient = HttpClient.newHttpClient();
            HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());

            String responseBody = response.body();
            return Double.parseDouble(responseBody);

        } catch (Exception e) {
            return 0.0;
        }
    }

    public static double profit_loss(String username) {
        try {
            String jsonbody = String.format("{\"username\":\"%s\"}", username);
            HttpRequest request = HttpRequest.newBuilder().uri(URI.create("http://localhost:5000/profit_loss_value")).header("Content-Type", "application/json").POST(HttpRequest.BodyPublishers.ofString(jsonbody)).build();
            HttpClient httpClient = HttpClient.newHttpClient();
            HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());

            String responseBody = response.body();
            return Double.parseDouble(responseBody);
        } catch (Exception e) {
            return 0.0;
        }
    }

    public static double total_investment(String username) {
        try {
            String jsonbody = String.format("{\"username\":\"%s\"}", username);
            HttpRequest request = HttpRequest.newBuilder().uri(URI.create("http://localhost:5000/investment_value")).header("Content-Type", "application/json").POST(HttpRequest.BodyPublishers.ofString(jsonbody)).build();
            HttpClient httpClient = HttpClient.newHttpClient();
            HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());

            String responseBody = response.body();
            return Double.parseDouble(responseBody);
        } catch (Exception e) {
            return 0.0;
        }
    }

    public static Map<String, String> currency_list() {
        try {
            HttpRequest request = HttpRequest.newBuilder()
                    .uri(URI.create("http://localhost:5000/exchange_rate"))
                    .POST(HttpRequest.BodyPublishers.noBody())
                    .build();

            HttpClient httpClient = HttpClient.newHttpClient();
            HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());

            String responseBody = response.body(); // e.g. ["Indian Rupee","US Dollar",...]

            Gson gson = new Gson();
            Type type = new TypeToken<Map<String, String>>() {}.getType();
            return gson.fromJson(response.body(), type);

        } catch (Exception e) {
            return new HashMap<>();
        }
    }



    public static double exchanged_value(String base_currency, String target_currency) {
        try {
            String jsonbody = String.format("{\"base_currency\":\"%s\",\"target_currency\":\"%s\"}", base_currency, target_currency);
            HttpRequest request = HttpRequest.newBuilder().uri(URI.create("http://localhost:5000/exchange_rate_value")).header("Content-Type", "application/json").POST(HttpRequest.BodyPublishers.ofString(jsonbody)).build();
            HttpClient httpClient = HttpClient.newHttpClient();
            HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());

            String responseBody = response.body();
            return Double.parseDouble(responseBody);
        } catch (Exception e) {
            return 0.0;
        }
    }

    public static List<List<Object>> get_stock(String username) {
        try {
            String jsonbody = String.format("{\"username\":\"%s\"}", username);
            HttpRequest request = HttpRequest.newBuilder().uri(URI.create("http://localhost:5000/get_stock_data")).header("Content-Type", "application/json").POST(HttpRequest.BodyPublishers.ofString(jsonbody)).build();
            HttpClient httpClient = HttpClient.newHttpClient();
            HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());

            Gson gson = new Gson();
            List<List<Object>> stockData = gson.fromJson(response.body(), new TypeToken<List<List<Object>>>() {
            }.getType());
            return stockData;
        } catch (Exception e) {
            return new ArrayList<>();
        }
    }

    public static JsonObject detailed_stock(String stock_name) {
        try {
            String jsonbody = String.format("{\"stock_name\":\"%s\"}", stock_name);
            HttpRequest request = HttpRequest.newBuilder().uri(URI.create("http://localhost:5000/detailed_stock_data")).header("Content-Type", "application/json").POST(HttpRequest.BodyPublishers.ofString(jsonbody)).build();
            HttpClient httpClient = HttpClient.newHttpClient();
            HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());
            Gson gson = new Gson();
            JsonObject stockData = gson.fromJson(response.body(), JsonObject.class);
            return stockData;
        } catch (Exception e) {
            return new JsonObject();
        }
    }


    public static void graph(String stock_name, LocalDate start_date, LocalDate end_date) {
        try {
            String jsonbody = String.format("{\"stock_name\":\"%s\",\"start_date\":\"%s\",\"end_date\":\"%s\"}",
                    stock_name, start_date.toString(), end_date.toString());

            System.out.println("DEBUG: Sending request with body:");
            System.out.println(jsonbody);

            HttpRequest request = HttpRequest.newBuilder()
                    .uri(URI.create("http://localhost:5000/plot_live_price"))
                    .header("Content-Type", "application/json")
                    .POST(HttpRequest.BodyPublishers.ofString(jsonbody))
                    .build();

            HttpClient httpClient = HttpClient.newHttpClient();
            HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());



        } catch (Exception e) {
            e.printStackTrace(); // Always print the exception!
        }
    }


    public static void stockname_graph(String username, String stockName, String mode,
                                       LocalDate startDate, LocalDate endDate, String month, String year) {
        try {
            System.out.println("success");
            Map<String, String> data = new HashMap<>();
            data.put("username", username);
            data.put("stock_name", stockName);
            data.put("mode", mode); // "daily", "monthly", or "yearly"

            if ("daily".equals(mode)) {
                data.put("start_date", startDate.toString());
                data.put("end_date", endDate.toString());
            } else if ("monthly".equals(mode)) {
                data.put("month", month);
                data.put("year", year);
            } else if ("yearly".equals(mode)) {
                data.put("year", year);
            }

            Gson gson = new Gson();
            String jsonBody = gson.toJson(data);

            HttpRequest request = HttpRequest.newBuilder()
                    .uri(URI.create("http://localhost:5000/plot_all_graphs"))
                    .header("Content-Type", "application/json")
                    .POST(HttpRequest.BodyPublishers.ofString(jsonBody))
                    .build();

            HttpClient httpClient = HttpClient.newHttpClient();
            httpClient.sendAsync(request, HttpResponse.BodyHandlers.ofString());

        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    public static String ml_prediction(String stock_name) {
        try {
            String jsonbody = String.format("{\"stock_name\":\"%s\"}", stock_name);

            HttpRequest request = HttpRequest.newBuilder()
                    .uri(URI.create("http://localhost:5000/predict"))
                    .header("Content-Type", "application/json")
                    .POST(HttpRequest.BodyPublishers.ofString(jsonbody))
                    .build();

            HttpClient httpClient = HttpClient.newHttpClient();
            HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());

            String responseBody = response.body();

            // Parse the response using Gson
            Gson gson = new Gson();
            JsonObject jsonObject = gson.fromJson(responseBody, JsonObject.class);

            String message1 = jsonObject.get("message1").getAsString();

            return message1;

        } catch (Exception e) {
            e.printStackTrace();
            return "Prediction failed.";
        }
    }


}

