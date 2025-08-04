package com.example.tradesight;

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.PreparedStatement;
import java.sql.SQLException;

public class Temp {
    public static void deleteStock(String username, String stockName) {
        String url = "jdbc:sqlite:../tradesight/stocks.db";
        String sql = "DELETE FROM Stocks WHERE Username = ? AND StockName = ?";

        try (Connection conn = DriverManager.getConnection(url);
             PreparedStatement pstmt = conn.prepareStatement(sql)) {

            pstmt.setString(1, username);
            pstmt.setString(2, stockName);

            int rowsAffected = pstmt.executeUpdate();
            if (rowsAffected > 0) {
                System.out.println("✅ Deleted " + rowsAffected + " row(s) for user '" + username + "' and stock '" + stockName + "'");
            } else {
                System.out.println("⚠️ No matching record found to delete.");
            }

        } catch (SQLException e) {
            System.err.println("❌ SQL error: " + e.getMessage());
        }
    }

    public static void main(String[] args) {
        deleteStock("v", "STATE BANK OF INDIA");
    }
}
