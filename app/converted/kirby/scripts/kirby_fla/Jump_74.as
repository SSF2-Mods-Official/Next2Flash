package kirby_fla
{
    import flash.display.MovieClip;

    public dynamic class Jump_74 extends MovieClip
    {

        public var hatBox:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var hitBox4:MovieClip;
        public var itemBox:MovieClip;
        public var self:KirbyExt;
        public var done:*;
        public var fatjump:*;

        public function Jump_74()
        {
            super();
            addFrameScript(0, this.frame1, 1, this.frame2, 21, this.frame22, 22, this.frame23, 23, this.frame24, 36, this.frame37, 37, this.frame38, 61, this.frame62);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as KirbyExt);
            if (parent && SSF2API.isReady() && this.self)
            {
                if (this.self.getGlobalVariable("screwAttackOn"))
                {
                    this.self.endAttack();
                    this.self.forceAttack("item_screw");
                }
                else
                {
                    this.done = false;
                    this.fatjump = false;
                    this.self.setGlobalVariable("kirbyPeachUsed", false);
                };
            };
        }

        internal function frame2():*
        {
            this.self.playSound("ssf2_snd_sfx_kirby_jump01");
        }

        internal function frame22():*
        {
            this.self.endAttack();
        }

        internal function frame23():*
        {
            this.fatjump = true;
        }

        internal function frame24():*
        {
            this.self.playSound("ssf2_snd_sfx_kirby_jump01");
        }

        internal function frame37():*
        {
            this.self.endAttack();
        }

        internal function frame38():*
        {
            if (this.fatjump)
            {
                this.self.stancePlayFrame("fatjump");
            };
        }

        internal function frame62():*
        {
            this.self.endAttack();
        }


    }
}

