// Decompiled by AS3 Sorcerer 6.20
// www.as3sorcerer.com

//fox_fla.fox_revival_20

package fox_fla
{
    import flash.display.MovieClip;

    public dynamic class fox_revival_20 extends MovieClip 
    {

        public var stance:MovieClip;
        public var self:FoxExt;

        public function fox_revival_20()
        {
            addFrameScript(0, this.frame1);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as FoxExt);
            if (SSF2API.isReady())
            {
                this.self.setGlobalVariable("canStartRise", true);
                this.self.setIntangibility(false);
            };
        }


    }
}//package fox_fla

