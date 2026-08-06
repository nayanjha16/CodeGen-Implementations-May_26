package org.example.patterns;
public class TicketIteratorTest {
    public static void main(String[] args) {
        TicketCollection col = new TicketCollection();
        col.add("a"); col.add("b");
        if (!col.join().equals("ticket:a:b")) throw new AssertionError(col.join());
        System.out.println("ok");
    }
}
