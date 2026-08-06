package org.example.patterns;
public class MetricsIspTest {
    public static void main(String[] args) {
        MetricsStore st = new MetricsStore();
        st.write("x");
        if (!MetricsIspClient.mirror(st).equals("metrics:x")) throw new AssertionError();
        System.out.println("ok");
    }
}
