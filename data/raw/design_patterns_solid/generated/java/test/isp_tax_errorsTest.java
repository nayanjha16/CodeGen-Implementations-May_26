package org.example.patterns;
public class TaxIspTest {
    public static void main(String[] args) {
        TaxStore st = new TaxStore();
        st.write("x");
        if (!TaxIspClient.mirror(st).equals("tax:x")) throw new AssertionError();
        System.out.println("ok");
    }
}
