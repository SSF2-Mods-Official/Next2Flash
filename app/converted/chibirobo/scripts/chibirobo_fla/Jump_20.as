package chibirobo_fla
{
    import flash.display.MovieClip;

    public dynamic class Jump_20 extends MovieClip
    {

        public var hand:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var itemBox:MovieClip;
        public var self:ChibiExt;
        public var xframe:*;
        public var done:*;

        public function Jump_20()
        {
            super();
            addFrameScript(0, this.frame1, 14, this.frame15);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as ChibiExt);
            this.xframe = "midair";
            this.done = false;
            if (SSF2API.isReady())
            {
                if (this.self.getGlobalVariable("screwAttackOn"))
                {
                    this.self.endAttack();
                    this.self.forceAttack("item_screw");
                }
                else
                {
                    this.self.playSound("jump_common");
                };
            };
        }

        internal function frame15():*
        {
            this.self.endAttack();
        }


    }
}

