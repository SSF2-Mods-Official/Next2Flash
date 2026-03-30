package
{
    import flash.display.MovieClip;

    public dynamic class simon_hud extends MovieClip
    {

        public var self:*;
        public var shake_start_x:Number;
        public var shake_start_y:Number;
        public var costumeData:*;
        public var camera:*;

        public function simon_hud()
        {
            super();
            addFrameScript(0, this.frame1, 1, this.frame2, 6, this.frame7, 17, this.frame18, 20, this.frame21, 33, this.frame34, 41, this.frame42, 44, this.frame45, 46, this.frame47, 76, this.frame77, 93, this.frame94, 135, this.frame136);
        }

        public function initShake():void
        {
            this.shake_start_x = x;
            this.shake_start_y = y;
            this.self.createTimer(1, 0, this.shake);
        }

        public function shake():void
        {
            x = (this.shake_start_x + SSF2API.safeRandomInteger(-4, 4));
            y = (this.shake_start_y + SSF2API.safeRandomInteger(-4, 4));
        }

        public function updatePalette(_arg_1:*=null):*
        {
            if (this.costumeData)
            {
                SSF2Utils.replacePalette(this, this.costumeData.paletteSwap);
            };
        }

        public function removeEvents(_arg_1:*=null):*
        {
            SSF2API.removeEventListener(SSF2Event.GAME_TICK_END, this.updatePalette);
        }

        internal function frame1():*
        {
            this.self = SSF2API.getCharacter(this);
            this.shake_start_x = 0;
            this.shake_start_y = 0;
            this.costumeData = new Object();
            if (SSF2API.isReady() && this.self)
            {
                this.costumeData = this.self.getPaletteSwapData();
                this.self.addEventListener(SSF2Event.STATE_CHANGE, this.removeEvents);
                SSF2API.addEventListener(SSF2Event.GAME_TICK_END, this.updatePalette);
                this.self.applyPalette(this);
            };
        }

        internal function frame2():*
        {
            this.camera = SSF2API.getCamera();
            this.camera.killDarkener(true);
        }

        internal function frame7():*
        {
            SSF2API.playSound("ssf2_snd_sfx_simon_attack_swing_l");
        }

        internal function frame18():*
        {
            this.initShake();
        }

        internal function frame21():*
        {
            this.self.destroyTimer(this.shake);
        }

        internal function frame34():*
        {
            if (!this.self.getMetalStatus())
            {
                this.self.playSound("ssf2_snd_vfx_simon_final_01", true);
            };
            SSF2API.playSound("ssf2_snd_sfx_simon_final_04");
        }

        internal function frame42():*
        {
        }

        internal function frame45():*
        {
            this.initShake();
        }

        internal function frame47():*
        {
            this.self.destroyTimer(this.shake);
        }

        internal function frame77():*
        {
            SSF2API.playSound("ssf2_snd_sfx_simon_final_05");
        }

        internal function frame94():*
        {
            if (!this.self.getMetalStatus())
            {
                this.self.playSound("ssf2_snd_vfx_simon_final_02", true);
            };
            this.initShake();
        }

        internal function frame136():*
        {
            stop();
            this.self.destroyTimer(this.shake);
            this.self.killFSCutscene();
            if (this.parent != null)
            {
                parent.removeChild(this);
            };
        }


    }
}

