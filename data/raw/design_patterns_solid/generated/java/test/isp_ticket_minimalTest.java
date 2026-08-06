package org.example.patterns;
public class TicketIspTest {
    public static void main(String[] args) {
        TicketStore st = new TicketStore();
        st.write("x");
        if (!TicketIspClient.mirror(st).equals("ticket:x")) throw new AssertionError();
        System.out.println("ok");
    }
}
