package chibirobo_fla
{
    import flash.display.MovieClip;

    public dynamic class FinalSmash_87 extends MovieClip
    {

        public var itemBox:MovieClip;
        public var self:ChibiExt;

        public function FinalSmash_87()
        {
            super();
            addFrameScript(0, this.frame1, 4, this.frame5, 14, this.frame15, 17, this.frame18, 18, this.frame19);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as ChibiExt);
        }

        internal function frame5():*
        {
            this.self.fireProjectile("gigarobo", this.self.getX(), SSF2API.getStage().getCameraBounds().y, true);
            this.self.playAttackSound(1);
        }

        internal function frame15():*
        {
        }

        internal function frame18():*
        {
            this.self.forceOnGround(5);
            if (!this.self.isOnGround())
            {
                this.self.resetMovement();
                this.self.updateAttackStats({"allowControl":true});
                this.self.resetJumps();
                this.self.toJump();
            };
        }

        internal function frame19():*
        {
            this.self.endAttack();
        }


    }
}

