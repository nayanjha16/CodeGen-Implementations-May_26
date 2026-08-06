package org.example.patterns;
public class PaymentsIspTest {
    public static void main(String[] args) {
        PaymentsStore st = new PaymentsStore();
        st.write("x");
        if (!PaymentsIspClient.mirror(st).equals("payments:x")) throw new AssertionError();
        System.out.println("ok");
    }
}
