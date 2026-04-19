// Decompiled by AS3 Sorcerer 6.20
// www.as3sorcerer.com

//fl.motion.DynamicMatrix

package fl.motion
{
    public class DynamicMatrix 
    {

        public static const MATRIX_ORDER_PREPEND:int = 0;
        public static const MATRIX_ORDER_APPEND:int = 1;

        protected var m_width:int;
        protected var m_height:int;
        protected var m_matrix:Array;

        public function DynamicMatrix(_arg_1:int, _arg_2:int)
        {
            this.Create(_arg_1, _arg_2);
        }

        protected function Create(_arg_1:int, _arg_2:int):void
        {
            var _local_3:int;
            var _local_4:int;
            if (((_arg_1 > 0) && (_arg_2 > 0)))
            {
                this.m_width = _arg_1;
                this.m_height = _arg_2;
                this.m_matrix = new Array(_arg_2);
                _local_3 = 0;
                while (_local_3 < _arg_2)
                {
                    this.m_matrix[_local_3] = new Array(_arg_1);
                    _local_4 = 0;
                    while (_local_4 < _arg_2)
                    {
                        this.m_matrix[_local_3][_local_4] = 0;
                        _local_4++;
                    };
                    _local_3++;
                };
            };
        }

        protected function Destroy():void
        {
            this.m_matrix = null;
        }

        public function GetWidth():Number
        {
            return (this.m_width);
        }

        public function GetHeight():Number
        {
            return (this.m_height);
        }

        public function GetValue(_arg_1:int, _arg_2:int):Number
        {
            var _local_3:Number = 0;
            if (((((_arg_1 >= 0) && (_arg_1 < this.m_height)) && (_arg_2 >= 0)) && (_arg_2 <= this.m_width)))
            {
                _local_3 = this.m_matrix[_arg_1][_arg_2];
            };
            return (_local_3);
        }

        public function SetValue(_arg_1:int, _arg_2:int, _arg_3:Number):void
        {
            if (((((_arg_1 >= 0) && (_arg_1 < this.m_height)) && (_arg_2 >= 0)) && (_arg_2 <= this.m_width)))
            {
                this.m_matrix[_arg_1][_arg_2] = _arg_3;
            };
        }

        public function LoadIdentity():void
        {
            var _local_1:int;
            var _local_2:int;
            if (this.m_matrix)
            {
                _local_1 = 0;
                while (_local_1 < this.m_height)
                {
                    _local_2 = 0;
                    while (_local_2 < this.m_width)
                    {
                        if (_local_1 == _local_2)
                        {
                            this.m_matrix[_local_1][_local_2] = 1;
                        }
                        else
                        {
                            this.m_matrix[_local_1][_local_2] = 0;
                        };
                        _local_2++;
                    };
                    _local_1++;
                };
            };
        }

        public function LoadZeros():void
        {
            var _local_1:int;
            var _local_2:int;
            if (this.m_matrix)
            {
                _local_1 = 0;
                while (_local_1 < this.m_height)
                {
                    _local_2 = 0;
                    while (_local_2 < this.m_width)
                    {
                        this.m_matrix[_local_1][_local_2] = 0;
                        _local_2++;
                    };
                    _local_1++;
                };
            };
        }

        public function Multiply(_arg_1:DynamicMatrix, _arg_2:int=0):Boolean
        {
            var _local_3:DynamicMatrix;
            var _local_4:int;
            var _local_5:int;
            var _local_7:int;
            var _local_8:int;
            var _local_6:Number = NaN;
            if (((!(this.m_matrix)) || (!(_arg_1))))
            {
                return (false);
            };
            var _local_9:int = _arg_1.GetHeight();
            var _local_10:int = _arg_1.GetWidth();
            if (_arg_2 == MATRIX_ORDER_APPEND)
            {
                if (this.m_width != _local_9)
                {
                    return (false);
                };
                _local_3 = new DynamicMatrix(_local_10, this.m_height);
                _local_4 = 0;
                while (_local_4 < this.m_height)
                {
                    _local_5 = 0;
                    while (_local_5 < _local_10)
                    {
                        _local_6 = 0;
                        _local_7 = 0;
                        _local_8 = 0;
                        while (((_local_7 < Math.max(this.m_height, _local_9)) && (_local_8 < Math.max(this.m_width, _local_10))))
                        {
                            _local_6 = (_local_6 + (_arg_1.GetValue(_local_7, _local_5) * this.m_matrix[_local_4][_local_8]));
                            _local_7++;
                            _local_8++;
                        };
                        _local_3.SetValue(_local_4, _local_5, _local_6);
                        _local_5++;
                    };
                    _local_4++;
                };
                this.Destroy();
                this.Create(_local_10, this.m_height);
                _local_4 = 0;
                while (_local_4 < _local_9)
                {
                    _local_5 = 0;
                    while (_local_5 < this.m_width)
                    {
                        this.m_matrix[_local_4][_local_5] = _local_3.GetValue(_local_4, _local_5);
                        _local_5++;
                    };
                    _local_4++;
                };
            }
            else
            {
                if (this.m_height != _local_10)
                {
                    return (false);
                };
                _local_3 = new DynamicMatrix(this.m_width, _local_9);
                _local_4 = 0;
                while (_local_4 < _local_9)
                {
                    _local_5 = 0;
                    while (_local_5 < this.m_width)
                    {
                        _local_6 = 0;
                        _local_7 = 0;
                        _local_8 = 0;
                        while (((_local_7 < Math.max(_local_9, this.m_height)) && (_local_8 < Math.max(_local_10, this.m_width))))
                        {
                            _local_6 = (_local_6 + (this.m_matrix[_local_7][_local_5] * _arg_1.GetValue(_local_4, _local_8)));
                            _local_7++;
                            _local_8++;
                        };
                        _local_3.SetValue(_local_4, _local_5, _local_6);
                        _local_5++;
                    };
                    _local_4++;
                };
                this.Destroy();
                this.Create(this.m_width, _local_9);
                _local_4 = 0;
                while (_local_4 < _local_9)
                {
                    _local_5 = 0;
                    while (_local_5 < this.m_width)
                    {
                        this.m_matrix[_local_4][_local_5] = _local_3.GetValue(_local_4, _local_5);
                        _local_5++;
                    };
                    _local_4++;
                };
            };
            return (true);
        }

        public function MultiplyNumber(_arg_1:Number):Boolean
        {
            var _local_2:int;
            var _local_3:Number = NaN;
            if (!this.m_matrix)
            {
                return (false);
            };
            var _local_4:int;
            while (_local_4 < this.m_height)
            {
                _local_2 = 0;
                while (_local_2 < this.m_width)
                {
                    _local_3 = 0;
                    _local_3 = (this.m_matrix[_local_4][_local_2] * _arg_1);
                    this.m_matrix[_local_4][_local_2] = _local_3;
                    _local_2++;
                };
                _local_4++;
            };
            return (true);
        }

        public function Add(_arg_1:DynamicMatrix):Boolean
        {
            var _local_2:int;
            var _local_3:Number = NaN;
            if (((!(this.m_matrix)) || (!(_arg_1))))
            {
                return (false);
            };
            var _local_4:int = _arg_1.GetHeight();
            var _local_5:int = _arg_1.GetWidth();
            if (((!(this.m_width == _local_5)) || (!(this.m_height == _local_4))))
            {
                return (false);
            };
            var _local_6:int;
            while (_local_6 < this.m_height)
            {
                _local_2 = 0;
                while (_local_2 < this.m_width)
                {
                    _local_3 = 0;
                    _local_3 = (this.m_matrix[_local_6][_local_2] + _arg_1.GetValue(_local_6, _local_2));
                    this.m_matrix[_local_6][_local_2] = _local_3;
                    _local_2++;
                };
                _local_6++;
            };
            return (true);
        }


    }
}//package fl.motion

