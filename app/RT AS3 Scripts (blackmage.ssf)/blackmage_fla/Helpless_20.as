// Decompiled by AS3 Sorcerer 6.20
// www.as3sorcerer.com

//blackmage_fla.Helpless_20

package blackmage_fla
{
    import flash.display.MovieClip;

    public dynamic class Helpless_20 extends MovieClip 
    {

        internal var hand:MovieClip;
        internal var hitBox:MovieClip;
        internal var hitBox2:MovieClip;
        internal var hitBox3:MovieClip;
        internal var itemBox:MovieClip;
        internal var self:BlackMageExt;

        public function Helpless_20()
        {
            addFrameScript(0, this.frame1, 5, this.frame6);
        }

        internal function frame1():*
        {
            var _local_1:MovieClip;
            var _local_2:MovieClip;
            var _local_3:MovieClip;
            var _local_4:MovieClip;
            var _local_5:MovieClip;
            var _local_6:BlackMageExt;
            this.self = (SSF2API.getCharacter(this) as BlackMageExt);
        }

        internal function frame6():*
        {
            this.self.stancePlayFrame("redo");
        }


    }
}//package blackmage_fla

