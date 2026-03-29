package
{
    public class Battlefield extends SSF2Stage
    {

        public function Battlefield(_arg_1:*):void
        {
            super(_arg_1);
        }

        override public function initialize():void
        {
            var _local_1:Array = [this.getBackground(), this.getForeground()];
            var _local_2:Array;
            var _local_3:Array = [this.getCameraBackgrounds()[0].mc];
            var _local_4:Array;
            var _local_5:Array;
            var _local_6:Array;
            SSF2StageQuality.init(_local_1, _local_2, _local_3, _local_4, _local_5, _local_6);
        }

        override public function update():void
        {
        }


    }
}

