package kirby_fla
{
    import flash.display.MovieClip;

    public dynamic class FinalSmash_177 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var self:KirbyExt;
        public var item:Array;
        public var fsController:KirbyFinalSmashController;
        public var camera:*;
        public var boil:*;

        public function FinalSmash_177()
        {
            super();
            addFrameScript(0, this.frame1, 1, this.frame2, 7, this.frame8, 18, this.frame19, 26, this.frame27, 34, this.frame35, 39, this.frame40, 40, this.frame41, 48, this.frame49, 52, this.frame53, 66, this.frame67, 70, this.frame71, 75, this.frame76, 80, this.frame81, 91, this.frame92, 98, this.frame99, 99, this.frame100, 123, this.frame124, 126, this.frame127, 127, this.frame128);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as KirbyExt);
            this.item = new Array();
            this.fsController = null;
            if (parent && SSF2API.isReady() && this.self)
            {
                this.self.playVoiceSound(1);
                this.self.playSound("kirby_fsdestroy");
                this.fsController = new KirbyFinalSmashController(this.self);
                this.self.createTimer(1, 0, this.fsController.update);
                this.self.camFocus(25);
                this.self.unnattachFromGround();
            };
        }

        internal function frame2():*
        {
            this.camera = SSF2API.getCamera();
            this.camera.killDarkener(true);
        }

        internal function frame8():*
        {
        }

        internal function frame19():*
        {
            this.self.playSound("kirby_fryingpan");
        }

        internal function frame27():*
        {
            this.self.playSound("kirby_fryingpan");
        }

        internal function frame35():*
        {
            this.self.playSound("kirby_jump1");
        }

        internal function frame40():*
        {
            this.boil = this.self.playSound("kirby_fsbg");
        }

        internal function frame41():*
        {
        }

        internal function frame49():*
        {
            this.self.playSound("kirby_fssalt");
        }

        internal function frame53():*
        {
            this.self.playSound("kirby_fssalt");
        }

        internal function frame67():*
        {
            this.self.playSound("kirby_fssalt");
        }

        internal function frame71():*
        {
            this.self.playSound("kirby_fssalt");
        }

        internal function frame76():*
        {
            this.self.stancePlayFrame("cook");
        }

        internal function frame81():*
        {
            SSF2API.stopSound(this.boil);
            this.self.playSound("kirby_jump1");
        }

        internal function frame92():*
        {
            this.self.updateAttackBoxStats(1, {
                "damage":12,
                "direction":75,
                "hasEffect":true,
                "hitStun":-1
            });
            this.self.refreshAttackID();
            this.self.playSound("splash_char");
            this.fsController.release();
        }

        internal function frame99():*
        {
            this.self.stancePlayFrame("items");
        }

        internal function frame100():*
        {
            this.self.playSound("kirby_fsdestroy");
        }

        internal function frame124():*
        {
            this.self.updateAttackStats({"ignorePlatformInfluence":false});
        }

        internal function frame127():*
        {
            this.self.forceOnGround(5);
            if (!this.self.isOnGround())
            {
                this.self.updateAttackStats({"allowControl":true});
                this.self.resetJumps();
                this.self.toJump();
            };
        }

        internal function frame128():*
        {
            this.self.endAttack();
        }


    }
}

