from datetime import datetime


class CurrencyAnalyzer:
    def __init__(self, filename):
        self.data = self.load_data(filename)

    def load_data(self, filename):
        records = []
        try:
            with open(filename, "r") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    parts = line.split()
                    if len(parts) < 2:
                        continue
                    try:
                        price = float(parts[-1])
                        date_str = " ".join(parts[:-1])
                        dt = datetime.strptime(date_str, "%B %d, %Y")
                        records.append({"date": dt, "price": price})
                    except ValueError:
                        continue
            records.sort(key=lambda x: x["date"])
            return records
        except FileNotFoundError:
            print(f"Error: File '{filename}' not found.")
            return []

    def get_price_by_date(self, target_date):
        for r in self.data:
            if r["date"] == target_date:
                return r["price"]
        return None

    def get_prices_in_range(self, start_date, end_date):
        """Returns a list of all prices between start and end (inclusive)."""
        return [r["price"] for r in self.data if start_date <= r["date"] <= end_date]

    def determine_pattern(self, prices):
        """
        Analyzes the internal steps of a price list.
        Returns: 'Monotonically Increasing', 'Monotonically Decreasing', or 'Mixed'
        """
        if len(prices) < 2:
            return "Stable/Single Point"

        is_increasing = True
        is_decreasing = True

        # Check every step against the previous step
        for i in range(1, len(prices)):
            if prices[i] > prices[i - 1]:
                is_decreasing = False
            elif prices[i] < prices[i - 1]:
                is_increasing = False

            # Optimization: If both flags are false, it's already mixed
            if not is_increasing and not is_decreasing:
                return "Mixed"

        if is_increasing:
            return "Monotonically Increasing"
        elif is_decreasing:
            return "Monotonically Decreasing"
        else:
            return "Stable (Flat)"

    def calculate_change(self, start_price, end_price):
        return ((end_price - start_price) / start_price) * 100

    def analyze(self, target_start_str, target_end_str, tolerance_percent=0.1):
        # 1. Parse Dates
        try:
            t_start = datetime.strptime(target_start_str, "%B %d, %Y")
            t_end = datetime.strptime(target_end_str, "%B %d, %Y")
        except ValueError:
            print("Error: Date format must be 'Month DD, YYYY'")
            return

        # 2. Get Target Data
        p_start = self.get_price_by_date(t_start)
        p_end = self.get_price_by_date(t_end)

        # Get the full list of prices inside this range to check pattern
        target_prices = self.get_prices_in_range(t_start, t_end)

        if p_start is None or p_end is None:
            print(
                f"Error: Could not find data for {target_start_str} or {target_end_str}"
            )
            return

        # 3. Analyze Target
        price_diff = p_end - p_start
        target_pct_change = self.calculate_change(p_start, p_end)
        days_diff = (t_end - t_start).days
        target_pattern = self.determine_pattern(target_prices)

        print(f"\n" + "=" * 50)
        print(f" ANALYSIS FOR: {target_start_str} -> {target_end_str}")
        print(f"=" * 50)
        print(f"Start Price:      {p_start:.5f}")
        print(f"End Price:        {p_end:.5f}")
        print(f"Duration:         {days_diff} days")
        print(f"Internal Data:    {len(target_prices)} data points found")
        print(f"-" * 50)
        print(f"Price Change:     {price_diff:.5f}")
        print(f"Percentage Move:  {target_pct_change:.4f}%")
        print(f"INTERNAL PATTERN: {target_pattern.upper()}")
        print(f"=" * 50)

        # 4. Scan History
        print(f"\nScanning history for matches...")
        print(
            f"Criteria: Move within +/- {tolerance_percent}% AND Pattern must be '{target_pattern}'"
        )

        found_matches = False

        for i in range(len(self.data)):
            start_record = self.data[i]

            # Find end record based on days difference
            end_record = None
            end_index = -1

            for j in range(i + 1, len(self.data)):
                time_delta = (self.data[j]["date"] - start_record["date"]).days
                if time_delta == days_diff:
                    end_record = self.data[j]
                    end_index = j
                    break
                if time_delta > days_diff:
                    break

            if end_record:
                # Skip self
                if start_record["date"] == t_start:
                    continue

                # A. Check Percentage Match
                historical_change = self.calculate_change(
                    start_record["price"], end_record["price"]
                )
                diff = abs(historical_change - target_pct_change)

                if diff <= tolerance_percent:
                    # B. Check Pattern Match
                    # Extract prices for this historical window
                    # We use slicing on the main list from start index (i) to end index (end_index)
                    hist_prices = [r["price"] for r in self.data[i : end_index + 1]]
                    hist_pattern = self.determine_pattern(hist_prices)

                    if hist_pattern == target_pattern:
                        found_matches = True
                        s_date = start_record["date"].strftime("%B %d, %Y")
                        e_date = end_record["date"].strftime("%B %d, %Y")
                        print(f"MATCH: {s_date} -> {e_date}")
                        print(
                            f"   Move: {historical_change:.4f}% (Diff: {diff:.4f}%) | Pattern: {hist_pattern}"
                        )

        if not found_matches:
            print("No historical matches found with matching pattern and percentage.")


# --- Usage ---

app = CurrencyAnalyzer("data/raw_data.txt")

start_date = "January 18, 2026"
end_date = "January 23, 2026"
tolerance = 0.1

app.analyze(start_date, end_date, tolerance)
