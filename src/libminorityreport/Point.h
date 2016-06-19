#ifndef MINORITYREPORT_POINT_H
#define MINORITYREPORT_POINT_H

class Point
{
public:
    Point(double x, double y) : _x(x), _y(y) {}
    ~Point() {}

    double X() { return _x; }
    double Y() { return _Y; }

private:
    double _x;
    double _y;
};

#endif