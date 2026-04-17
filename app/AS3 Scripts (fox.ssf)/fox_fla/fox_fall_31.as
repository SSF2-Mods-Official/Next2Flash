// Decompiled by AS3 Sorcerer 6.20
// www.as3sorcerer.com

//fox_fla.fox_fall_31

package fox_fla
{
    import flash.display.MovieClip;

    public dynamic class fox_fall_31 extends MovieClip 
    {

        public var hand:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var hitBox4:MovieClip;
        public var itemBox:MovieClip;
        public var self:FoxExt;

        public function fox_fall_31()
        {
            addFrameScript(0, this.frame1, 4, this.frame5);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as FoxExt);
            if (((SSF2API.isReady()) && (this.self)))
            {
                this.self.stancePlayFrame("redo");
            };
        }

        internal function frame5():*
        {
            this.self.stancePlayFrame("redo");
        }


    }
}//package fox_fla

