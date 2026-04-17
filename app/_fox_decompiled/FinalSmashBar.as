package
{
    import flash.display.MovieClip;

    public class FinalSmashBar
    {

        private var _value:Number;
        private var _maxValue:Number;
        private var _movieClip:*;

        public function FinalSmashBar(_arg_1:Number)
        {
            this._value = _arg_1;
            this._maxValue = _arg_1;
        }

        public function addToDamageMeter(_arg_1:MovieClip):*
        {
            this._movieClip = _arg_1.addChild(SSF2API.getMCByLinkageName("fs_bar"));
            this._movieClip.x = 1.35;
            this._movieClip.y = 41.4;
        }

        public function removeFromDamageMeter(_arg_1:MovieClip):*
        {
            _arg_1.removeChild(this._movieClip);
        }

        public function updateBar(_arg_1:Number):*
        {
            this._value = _arg_1;
            this._movieClip.bar.scaleX = (this._value / this._maxValue);
            SSF2API.print(((this._value.toString() + " ") + this._maxValue.toString()));
        }


    }
}

