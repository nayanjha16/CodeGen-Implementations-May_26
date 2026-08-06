package org.example.patterns;
public class DatabaseDipTest {
    public static void main(String[] args) {
        String out = new DatabaseAppService(new DatabaseHttpGateway()).publish("p");
        if (!out.equals("http-database:p")) throw new AssertionError(out);
        System.out.println("ok");
    }
}
