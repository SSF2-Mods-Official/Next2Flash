// Decompiled by AS3 Sorcerer 6.20
// www.as3sorcerer.com

//blackmage_fla.Stunned_120

package blackmage_fla
{
    import flash.display.MovieClip;

    public dynamic class Stunned_120 extends MovieClip 
    {

        internal var hitBox:MovieClip;
        internal var hitBox2:MovieClip;
        internal var itemBox:MovieClip;
        internal var self:BlackMageExt;

        public function Stunned_120()
        {
            addFrameScript(0, this.frame1, 25, this.frame26);
        }

        internal function frame1():*
        {
            var _local_1:MovieClip;
            var _local_2:MovieClip;
            var _local_3:MovieClip;
            var _local_4:BlackMageExt;
            this.self = (SSF2API.getCharacter(this) as BlackMageExt);
            if (((parent) && (SSF2API.isReady())))
            {
                this.self.playSound("bm_Dizzy");
                this.self.setGlobalVariable("jab", false);
            };
        }

        internal function frame26():*
        {
            this.self.stancePlayFrame("again");
        }


    }
}//package blackmage_fla

