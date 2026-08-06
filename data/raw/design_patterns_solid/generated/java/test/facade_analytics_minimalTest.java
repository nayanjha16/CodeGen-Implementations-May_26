package org.example.patterns;
public class AnalyticsFacadeTest {
    public static void main(String[] args) {
        AnalyticsFacade f = new AnalyticsFacade();
        if (!f.submit("x").equals("wrote-analytics:x")) throw new AssertionError();
        System.out.println("ok");
    }
}
