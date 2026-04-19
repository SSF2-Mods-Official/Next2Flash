// Decompiled by AS3 Sorcerer 6.20
// www.as3sorcerer.com

//blackmage_fla.Win_12

package blackmage_fla
{
    import flash.display.MovieClip;

    public dynamic class Win_12 extends MovieClip 
    {

        internal var self:BlackMageExt;

        public function Win_12()
        {
            addFrameScript(0, this.frame1, 125, this.frame126);
        }

        internal function frame1():*
        {
            var _local_1:BlackMageExt;
            this.self = (SSF2API.getCharacter(this) as BlackMageExt);
        }

        internal function frame126():*
        {
            gotoAndPlay("loop");
        }


    }
}//package blackmage_fla

