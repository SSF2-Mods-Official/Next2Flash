// Decompiled by AS3 Sorcerer 6.20
// www.as3sorcerer.com

//fox_fla.fox_roll_118

package fox_fla
{
    import flash.display.MovieClip;

    public dynamic class fox_roll_118 extends MovieClip 
    {

        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var hitBox4:MovieClip;
        public var itemBox:MovieClip;
        public var self:FoxExt;

        public function fox_roll_118()
        {
            addFrameScript(0, this.frame1, 10, this.frame11, 17, this.frame18);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as FoxExt);
            if (((SSF2API.isReady()) && (this.self)))
            {
                this.self.setIntangibility(true);
            };
        }

        internal function frame11():*
        {
            this.self.setIntangibility(false);
        }

        internal function frame18():*
        {
            this.self.endAttack();
        }


    }
}//package fox_fla

