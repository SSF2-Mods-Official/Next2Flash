package simon_fla
{
    import flash.display.MovieClip;

    public dynamic class Dizzy_81 extends MovieClip
    {

        public var dizzy_stars:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var hitBox4:MovieClip;
        public var itemBox:MovieClip;
        public var self:SimonExt;

        public function Dizzy_81()
        {
            super();
            addFrameScript(0, this.frame1, 41, this.frame42);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as SimonExt);
            if (parent && SSF2API.isReady() && this.self && !this.self.getMetalStatus())
            {
                this.self.playSound("ssf2_snd_vfx_simon_hurt02", true);
            };
        }

        internal function frame42():*
        {
            this.self.stancePlayFrame("again");
        }


    }
}

