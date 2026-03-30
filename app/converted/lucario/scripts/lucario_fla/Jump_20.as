package lucario_fla
{
    import flash.display.MovieClip;

    public dynamic class Jump_20 extends MovieClip
    {

        public var aura1:MovieClip;
        public var aura2:MovieClip;
        public var hand:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var itemBox:MovieClip;
        public var self:LucarioExt;
        public var xframe:*;
        public var done:*;

        public function Jump_20()
        {
            super();
            addFrameScript(0, this.frame1, 1, this.frame2, 17, this.frame18, 33, this.frame34);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as LucarioExt);
            this.xframe = "midair";
            this.done = false;
            if (SSF2API.isReady() && this.self)
            {
                if (this.self.getGlobalVariable("screwAttackOn"))
                {
                    this.self.endAttack();
                    this.self.forceAttack("item_screw");
                }
                else
                {
                    this.self.updateAuraPaws();
                };
            };
        }

        internal function frame2():*
        {
            if (!this.self.getMetalStatus())
            {
                this.self.playSound("ucario_jump_vc", true);
            };
        }

        internal function frame18():*
        {
            this.self.endAttack();
        }

        internal function frame34():*
        {
            this.self.endAttack();
        }


    }
}

