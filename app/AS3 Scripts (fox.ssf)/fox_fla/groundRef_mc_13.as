// Decompiled by AS3 Sorcerer 6.20
// www.as3sorcerer.com

//fox_fla.groundRef_mc_13

package fox_fla
{
    import flash.display.MovieClip;

    public dynamic class groundRef_mc_13 extends MovieClip 
    {

        public var self:FoxExt;

        public function groundRef_mc_13()
        {
            addFrameScript(0, this.frame1);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as FoxExt);
            this.visible = false;
        }


    }
}//package fox_fla

