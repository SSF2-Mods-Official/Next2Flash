// Decompiled by AS3 Sorcerer 6.20
// www.as3sorcerer.com

//SSF2Enemy

package 
{
    public class SSF2Enemy extends SSF2GameObject 
    {

        public function SSF2Enemy(_arg_1:*):void
        {
            super(_arg_1);
        }

        override public function getType():String
        {
            return ("SSF2Enemy");
        }

        override public function inState(_arg_1:uint):Boolean
        {
            if (isDisposed())
            {
                SSF2API.print((("Warning: API attempted to check inState(EState." + EState.toString(_arg_1)) + ") after object has been disposed!"));
                return (_arg_1 === 1);
            };
            return (super.inState(_arg_1));
        }

        override public function setState(_arg_1:uint):void
        {
            if ((_arg_1 === 1))
            {
                SSF2API.print("Warning: Cannot explicitly set SSF2Enemy to DEAD state. Please use destroy() method instead.");
            };
            super.setState(_arg_1);
        }

        public function destroy():void
        {
            _api.destroy();
        }

        public function getOwner():*
        {
            return (_api.getOwner());
        }

        public function setOwner(_arg_1:*):void
        {
            _api.setOwner(_arg_1);
        }

        public function fireProjectile(_arg_1:*, _arg_2:Number=0, _arg_3:Number=0, _arg_4:Boolean=false, _arg_5:Object=null):*
        {
            return (_api.fireProjectile(_arg_1, _arg_2, _arg_3, _arg_4, _arg_5));
        }

        public function getEnemyStat(_arg_1:String):*
        {
            return (_api.getEnemyStat(_arg_1));
        }

        public function updateEnemyStats(_arg_1:Object):void
        {
            _api.updateEnemyStats(_arg_1);
        }

        public function setHurtInterrupt(_arg_1:Function):void
        {
            _api.setHurtInterrupt(_arg_1);
        }


    }
}//package 

