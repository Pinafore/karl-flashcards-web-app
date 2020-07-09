
export {}

declare global {
  interface Date {
    toIsoString(): string;
  }
}

Date.prototype.toIsoString = function() {
  const tzo = -this.getTimezoneOffset(),
    dif = tzo >= 0 ? "+" : "-",
    pad = function(num) {
      const norm = Math.floor(Math.abs(num));
      return (norm < 10 ? "0" : "") + norm;
    };
  return this.getFullYear() +
    '-' + pad(this.getMonth() + 1) +
    '-' + pad(this.getDate()) +
    'T' + pad(this.getHours()) +
    ':' + pad(this.getMinutes()) +
    ':' + pad(this.getSeconds()) +
    dif + pad(tzo / 60) +
    ':' + pad(tzo % 60);
};
