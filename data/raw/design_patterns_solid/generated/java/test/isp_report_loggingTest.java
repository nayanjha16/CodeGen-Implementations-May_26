package org.example.patterns;
public class ReportIspTest {
    public static void main(String[] args) {
        ReportStore st = new ReportStore();
        st.write("x");
        if (!ReportIspClient.mirror(st).equals("report:x")) throw new AssertionError();
        System.out.println("ok");
    }
}
