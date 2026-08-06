package org.example.patterns;
public class TicketAbstractFactoryTest {
    public static void main(String[] args) {
        String out = TicketAbstractFactoryDemo.run(new TicketCloudFactory());
        if (!out.equals("cloud-btn-ticket|cloud-dlg-ticket")) throw new AssertionError(out);
        System.out.println("ok");
    }
}
