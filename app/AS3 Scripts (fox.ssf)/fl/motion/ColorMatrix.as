// Decompiled by AS3 Sorcerer 6.20
// www.as3sorcerer.com

//fl.motion.ColorMatrix

package fl.motion
{
    public class ColorMatrix extends DynamicMatrix 
    {

        protected static const LUMINANCER:Number = 0.3086;
        protected static const LUMINANCEG:Number = 0.6094;
        protected static const LUMINANCEB:Number = 0.082;

        public function ColorMatrix()
        {
            super(5, 5);
            LoadIdentity();
        }

        public function SetBrightnessMatrix(_arg_1:Number):void
        {
            if (!m_matrix)
            {
                return;
            };
            m_matrix[0][4] = _arg_1;
            m_matrix[1][4] = _arg_1;
            m_matrix[2][4] = _arg_1;
        }

        public function SetContrastMatrix(_arg_1:Number):void
        {
            if (!m_matrix)
            {
                return;
            };
            var _local_2:Number = (0.5 * (127 - _arg_1));
            _arg_1 = (_arg_1 / 127);
            m_matrix[0][0] = _arg_1;
            m_matrix[1][1] = _arg_1;
            m_matrix[2][2] = _arg_1;
            m_matrix[0][4] = _local_2;
            m_matrix[1][4] = _local_2;
            m_matrix[2][4] = _local_2;
        }

        public function SetSaturationMatrix(_arg_1:Number):void
        {
            if (!m_matrix)
            {
                return;
            };
            var _local_2:Number = (1 - _arg_1);
            var _local_3:Number = (_local_2 * LUMINANCER);
            m_matrix[0][0] = (_local_3 + _arg_1);
            m_matrix[1][0] = _local_3;
            m_matrix[2][0] = _local_3;
            _local_3 = (_local_2 * LUMINANCEG);
            m_matrix[0][1] = _local_3;
            m_matrix[1][1] = (_local_3 + _arg_1);
            m_matrix[2][1] = _local_3;
            _local_3 = (_local_2 * LUMINANCEB);
            m_matrix[0][2] = _local_3;
            m_matrix[1][2] = _local_3;
            m_matrix[2][2] = (_local_3 + _arg_1);
        }

        public function SetHueMatrix(_arg_1:Number):void
        {
            var _local_11:int;
            if (!m_matrix)
            {
                return;
            };
            LoadIdentity();
            var _local_2:DynamicMatrix = new DynamicMatrix(3, 3);
            var _local_3:DynamicMatrix = new DynamicMatrix(3, 3);
            var _local_4:DynamicMatrix = new DynamicMatrix(3, 3);
            var _local_5:Number = Math.cos(_arg_1);
            var _local_6:Number = Math.sin(_arg_1);
            var _local_7:Number = 0.213;
            var _local_8:Number = 0.715;
            var _local_9:Number = 0.072;
            _local_2.SetValue(0, 0, _local_7);
            _local_2.SetValue(1, 0, _local_7);
            _local_2.SetValue(2, 0, _local_7);
            _local_2.SetValue(0, 1, _local_8);
            _local_2.SetValue(1, 1, _local_8);
            _local_2.SetValue(2, 1, _local_8);
            _local_2.SetValue(0, 2, _local_9);
            _local_2.SetValue(1, 2, _local_9);
            _local_2.SetValue(2, 2, _local_9);
            _local_3.SetValue(0, 0, (1 - _local_7));
            _local_3.SetValue(1, 0, -(_local_7));
            _local_3.SetValue(2, 0, -(_local_7));
            _local_3.SetValue(0, 1, -(_local_8));
            _local_3.SetValue(1, 1, (1 - _local_8));
            _local_3.SetValue(2, 1, -(_local_8));
            _local_3.SetValue(0, 2, -(_local_9));
            _local_3.SetValue(1, 2, -(_local_9));
            _local_3.SetValue(2, 2, (1 - _local_9));
            _local_3.MultiplyNumber(_local_5);
            _local_4.SetValue(0, 0, -(_local_7));
            _local_4.SetValue(1, 0, 0.143);
            _local_4.SetValue(2, 0, -(1 - _local_7));
            _local_4.SetValue(0, 1, -(_local_8));
            _local_4.SetValue(1, 1, 0.14);
            _local_4.SetValue(2, 1, _local_8);
            _local_4.SetValue(0, 2, (1 - _local_9));
            _local_4.SetValue(1, 2, -0.283);
            _local_4.SetValue(2, 2, _local_9);
            _local_4.MultiplyNumber(_local_6);
            _local_2.Add(_local_3);
            _local_2.Add(_local_4);
            var _local_10:int;
            while (_local_10 < 3)
            {
                _local_11 = 0;
                while (_local_11 < 3)
                {
                    m_matrix[_local_10][_local_11] = _local_2.GetValue(_local_10, _local_11);
                    _local_11++;
                };
                _local_10++;
            };
        }

        public function GetFlatArray():Array
        {
            var _local_4:int;
            if (!m_matrix)
            {
                return (null);
            };
            var _local_1:Array = new Array();
            var _local_2:int;
            var _local_3:int;
            while (_local_3 < 4)
            {
                _local_4 = 0;
                while (_local_4 < 5)
                {
                    _local_1[_local_2] = m_matrix[_local_3][_local_4];
                    _local_2++;
                    _local_4++;
                };
                _local_3++;
            };
            return (_local_1);
        }


    }
}//package fl.motion

class XFormData 
{

    public var ox:Number;
    public var oy:Number;
    public var oz:Number;


}


