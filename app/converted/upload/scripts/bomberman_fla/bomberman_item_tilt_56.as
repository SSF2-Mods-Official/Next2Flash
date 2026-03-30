package bomberman_fla
{
    import flash.display.MovieClip;

    public dynamic class bomberman_item_tilt_56 extends MovieClip
    {

        public var hitBox:MovieClip;
        public var itemBox:MovieClip;
        public var self:BombermanExt;

        public function bomberman_item_tilt_56()
        {
            super();
            addFrameScript(0, this.frame1, 6, this.frame7, 8, this.frame9, 18, this.frame19);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as BombermanExt);
        }

        internal function frame7():*
        {
            this.self.getItem().activateItem();
            this.self.playAttackSound(1);
            this.self.attachEffect("global_dust_heavy", {
                "x":this.self.flipX(-7),
                "y":3,
                "scaleX":-0.5,
                "scaleY":-0.5
            });
        }

        internal function frame9():*
        {
            this.self.getItem().deactivateItem();
        }

        internal function frame19():*
        {
            this.self.endAttack();
        }


    }
}

