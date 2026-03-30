package simon_fla
{
    import flash.display.MovieClip;

    public dynamic class Jump_16 extends MovieClip
    {

        public var hand:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var hitBox4:MovieClip;
        public var itemBox:MovieClip;
        public var self:SimonExt;

        public function Jump_16()
        {
            super();
            addFrameScript(0, this.frame1, 2, this.frame3, 16, this.frame17);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as SimonExt);
            if (SSF2API.isReady() && this.self)
            {
                if (this.self.getGlobalVariable("screwAttackOn"))
                {
                    this.self.endAttack();
                    this.self.forceAttack("item_screw");
                }
                else
                {
                    SSF2API.playSound("ssf2_snd_sfx_simon_jump01");
                };
            };
        }

        internal function frame3():*
        {
        }

        internal function frame17():*
        {
            this.self.endAttack();
        }


    }
}

