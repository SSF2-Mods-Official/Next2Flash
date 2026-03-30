package dedede_fla
{
    import flash.display.MovieClip;

    public dynamic class Skid_35 extends MovieClip
    {

        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var hitBox4:MovieClip;
        public var itemBox:MovieClip;
        public var self:DededeExt;

        public function Skid_35()
        {
            super();
            addFrameScript(0, this.frame1, 6, this.frame7);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as DededeExt);
            if (SSF2API.isReady() && this.self)
            {
                this.self.playSound("ssf2_snd_sfx_dedede_runstop");
                SSF2API.getCamera().shake(2);
            };
        }

        internal function frame7():*
        {
            this.self.endAttack();
        }


    }
}

