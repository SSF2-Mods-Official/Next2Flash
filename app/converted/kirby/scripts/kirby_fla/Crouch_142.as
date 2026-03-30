package kirby_fla
{
    import flash.display.MovieClip;

    public dynamic class Crouch_142 extends MovieClip
    {

        public var hatBox:MovieClip;
        public var hitBox:MovieClip;
        public var itemBox:MovieClip;
        public var self:KirbyExt;

        public function Crouch_142()
        {
            super();
            addFrameScript(0, this.frame1, 2, this.frame3, 5, this.frame6);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as KirbyExt);
            if (parent && SSF2API.isReady() && this.self)
            {
                SSF2API.playSound("ssf2_snd_sfx_kirby_crouch_start");
            };
        }

        internal function frame3():*
        {
            this.self.setGlobalVariable("crouchdown", true);
        }

        internal function frame6():*
        {
            this.self.stancePlayFrame("loop");
        }


    }
}

