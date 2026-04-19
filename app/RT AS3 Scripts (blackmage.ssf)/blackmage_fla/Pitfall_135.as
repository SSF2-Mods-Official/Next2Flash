// Decompiled by AS3 Sorcerer 6.20
// www.as3sorcerer.com

//blackmage_fla.Pitfall_135

package blackmage_fla
{
    import flash.display.MovieClip;

    public dynamic class Pitfall_135 extends MovieClip 
    {

        internal var hitBox:MovieClip;
        internal var hitBox2:MovieClip;
        internal var itemBox:MovieClip;
        internal var self:BlackMageExt;

        public function Pitfall_135()
        {
            addFrameScript(0, this.frame1);
        }

        internal function frame1():*
        {
            var _local_1:MovieClip;
            var _local_2:MovieClip;
            var _local_3:MovieClip;
            var _local_4:BlackMageExt;
            if (SSF2API.isReady())
            {
                this.self = (SSF2API.getCharacter(this) as BlackMageExt);
            };
            if (((parent) && (SSF2API.isReady())))
            {
                this.self.setGlobalVariable("jab", false);
            };
        }


    }
}//package blackmage_fla

