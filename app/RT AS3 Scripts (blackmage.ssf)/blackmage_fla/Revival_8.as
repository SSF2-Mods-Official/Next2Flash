// Decompiled by AS3 Sorcerer 6.20
// www.as3sorcerer.com

//blackmage_fla.Revival_8

package blackmage_fla
{
    import flash.display.MovieClip;

    public dynamic class Revival_8 extends MovieClip 
    {

        internal var self:BlackMageExt;

        public function Revival_8()
        {
            addFrameScript(0, this.frame1);
        }

        internal function frame1():*
        {
            var _local_1:BlackMageExt;
            this.self = (SSF2API.getCharacter(this) as BlackMageExt);
            if (SSF2API.isReady())
            {
                this.self.setGlobalVariable("canStartRise", true);
            };
        }


    }
}//package blackmage_fla

