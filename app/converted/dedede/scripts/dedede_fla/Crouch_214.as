package dedede_fla
{
    import flash.display.MovieClip;

    public dynamic class Crouch_214 extends MovieClip
    {

        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var hitBox4:MovieClip;
        public var hitBox5:MovieClip;
        public var itemBox:MovieClip;
        public var self:DededeExt;

        public function Crouch_214()
        {
            super();
            addFrameScript(0, this.frame1, 1, this.frame2, 3, this.frame4, 4, this.frame5, 5, this.frame6);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as DededeExt);
        }

        internal function frame2():*
        {
            this.self.playSound("ssf2_snd_sfx_dedede_step01");
        }

        internal function frame4():*
        {
            this.self.playSound("ssf2_snd_sfx_dedede_step02");
        }

        internal function frame5():*
        {
            this.self.setGlobalVariable("crouchdown", true);
        }

        internal function frame6():*
        {
            gotoAndStop("loop");
        }


    }
}

