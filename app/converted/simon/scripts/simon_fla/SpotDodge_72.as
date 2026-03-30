package simon_fla
{
    import flash.display.MovieClip;

    public dynamic class SpotDodge_72 extends MovieClip
    {

        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var hitBox4:MovieClip;
        public var itemBox:MovieClip;
        public var self:SimonExt;

        public function SpotDodge_72()
        {
            super();
            addFrameScript(0, this.frame1, 1, this.frame2, 8, this.frame9, 14, this.frame15);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as SimonExt);
        }

        internal function frame2():*
        {
            this.self.setIntangibility(true);
            this.self.attachEffect("global_dust_cloud", {
                "scaleX":0.8,
                "scaleY":0.8
            });
        }

        internal function frame9():*
        {
            this.self.setIntangibility(false);
        }

        internal function frame15():*
        {
            this.self.endAttack();
        }


    }
}

