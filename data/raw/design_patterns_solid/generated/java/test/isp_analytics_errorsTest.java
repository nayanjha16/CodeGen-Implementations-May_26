package org.example.patterns;
public class AnalyticsIspTest {
    public static void main(String[] args) {
        AnalyticsStore st = new AnalyticsStore();
        st.write("x");
        if (!AnalyticsIspClient.mirror(st).equals("analytics:x")) throw new AssertionError();
        System.out.println("ok");
    }
}
