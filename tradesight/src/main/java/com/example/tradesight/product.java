package com.example.tradesight;

import java.util.Date;

public class product {

    private String stockname;
    private int quantity;
    private double pricebuy;
    private Date date;
    private double currprice;
    private double profitloss;
    private String change;

    public product(){
        this.stockname = "";
        this.quantity = 0;
        this.pricebuy = 0;
        this.date = new Date();
        this.currprice = 0;
        this.profitloss = 0;
        this.change = "";
    }
    public product(String stockname, int quantity, double pricebuy, Date date, double currprice, double profitloss, String change){
        this.stockname = stockname;
        this.quantity = quantity;
        this.pricebuy = pricebuy;
        this.date = date;
        this.currprice = currprice;
        this.profitloss = profitloss;
        this.change = change;
    }

    public String getStockname() {
        return stockname;
    }

    public void setStockname(String stockname) {
        this.stockname = stockname;
    }

    public int getQuantity() {
        return quantity;
    }

    public void setQuantity(int quantity) {
        this.quantity = quantity;
    }

    public double getPricebuy() {
        return pricebuy;
    }

    public void setPricebuy(double pricebuy) {
        this.pricebuy = pricebuy;
    }

    public double getCurrprice() {
        return currprice;
    }

    public void setCurrprice(double currprice) {
        this.currprice = currprice;
    }

    public double getProfitloss() {
        return profitloss;
    }

    public void setProfitloss(double profitloss) {
        this.profitloss = profitloss;
    }

    public String getChange() {
        return change;
    }

    public Date getDate() {
        return date;
    }

    public void setDate(Date date) {
        this.date = date;
    }

    public void setChange(String change) {
        this.change = change;
    }
}
